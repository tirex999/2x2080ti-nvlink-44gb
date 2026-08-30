#!/bin/bash
# Боевой запуск Qwen3.8-Flash-Next на двух 2080 Ti (44 ГБ видеопамяти) и 140 ГБ ОЗУ.
#
# ПОЧЕМУ КОМАНДА ВЫНЕСЕНА В СКРИПТ, А НЕ НАПИСАНА В ExecStart.
# systemd портит обратные слэши в аргументах — в журнале появляется
# "Ignoring unknown escape sequences", — а здесь они несут смысл: это регулярки.
#
# РАСКЛАДКА. Двенадцать слоёв экспертов уезжают на карты: 0-7 на первую,
# 8-11 на вторую. Остальные эксперты и n-грамм-таблица per_layer_token_embd
# (28.8 ГБ) остаются в оперативке. Больше двенадцати слоёв не влезает.
# Правила ОБЯЗАТЕЛЬНО одним флагом через запятую: при нескольких -ot сервер
# берёт только последний и пишет об этом DEPRECATED в журнал.
#
# ПОТОКИ. -t 32 для генерации: она упирается в пропускную способность памяти,
# и лишние потоки ей мешают (32 обыграли 64 и 96 на всех замерах).
# -tb 144 для обработки промпта: она упирается в вычисления и хочет все ядра.
#
# --load-mode mlock ОБЯЗАТЕЛЕН, если модель лежит на сетевом хранилище:
# mmap поверх NFS даёт 0.07 t/s. Проверять по факту, а не по флагу:
#     grep VmLck /proc/$(pgrep -f llama-server)/status
# должен показать объём модели. Юниту нужен LimitMEMLOCK=infinity, иначе
# mlock молча не сработает и сервер продолжит через mmap.
#
# --reasoning-format none оставляет рассуждение прямо в тексте ответа.
# По умолчанию оно уезжает в отдельное поле reasoning_content, которое
# веб-интерфейс не рисует, и это выглядит как зависший сервер.

MODEL=${MODEL:-/LLM/models/lmstudio-community/Qwen3.8-Flash-Next-GGUF/Qwen3.8-Flash-Next-Q4_K_M-00001-of-00003.gguf}
BIN=${BIN:-/root/llama.cpp-next/build/bin/llama-server}
PORT=${PORT:-8080}

exec "$BIN" -m "$MODEL" \
  --alias qwen38-next --host 0.0.0.0 --port "$PORT" \
  -ngl 99 --load-mode mlock -fa on \
  --numa distribute -t 32 -tb 144 \
  --reasoning-format none \
  -c 32768 \
  -ot 'per_layer_token_embd\.weight=CPU,blk\.[0-7]\.ffn_.*_exps\.weight=CUDA0,blk\.[89]\.ffn_.*_exps\.weight=CUDA1,blk\.1[01]\.ffn_.*_exps\.weight=CUDA1,ffn_.*_exps\.weight=CPU'
