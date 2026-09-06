#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Врезка в FreeToken: префилл MoE считает процессор (AVX-512), а не карта.

Штатно FreeToken отдаёт процессору только генерацию, а префилл гонит целые слои
экспертов на карту через PCIe. На Flash-Next NVFP4 это 63 ГБ за проход и 0.62 т/с
префилла против 79 т/с на процессоре. Разбор — в docs/results.md, раздел 13.

Правятся два файла в venv:
  engine/engine.py    — черновики процессорного исполнителя размечены как
                        max_tokens*top_k*I, а max_tokens берётся из
                        --max-running-requests, то есть единица. Расширяем до
                        FT_CPU_PREFILL, иначе подача батча = запись за границу.
  layers/moe.py       — в _prefill_routed добавляется процессорная ветвь: тот же
                        cache.cpu_executor.decode, чанками по FT_CPU_PREFILL.

Запуск:   python3 ft-cpu-prefill.py [путь-к-site-packages/freetoken]
Откат:    python3 ft-cpu-prefill.py --revert [путь]
Включение после врезки:  export FT_CPU_PREFILL=256  (0 или снятие = штатный путь)
Проверка: в журнале при старте должно быть max_tokens=256, а не max_tokens=1.

Обновление пакета FreeToken врезку снесёт — прогнать заново.
"""
import os
import shutil
import sys

PO_UMOLCHANIYU = "/root/ft-venv/lib/python3.10/site-packages/freetoken"
BACKUP = ".pered_vrezkoy"

ENGINE_BYLO = "        max_tokens = max(config.max_running_req, config.cuda_graph_max_bs or 0, 1)\n"
ENGINE_STALO = ENGINE_BYLO + (
    "        # ВРЕЗКА (префилл на процессоре): черновики в C++ размечены как\n"
    "        # max_tokens*top_k*I, поэтому под префилл-чанк их надо расширить,\n"
    "        # иначе запись за границу буфера.\n"
    '        _ft_pf = int(os.environ.get("FT_CPU_PREFILL", "0") or 0)\n'
    "        if _ft_pf > 0:\n"
    "            max_tokens = max(max_tokens, _ft_pf)\n"
)

HELPER_BYLO = "class OffloadMoELayer(MoELayer):"
HELPER_STALO = (
    "_CPU_PREFILL_CHUNK = None\n"
    "\n"
    "\n"
    "def _cpu_prefill_chunk() -> int:\n"
    '    """ВРЕЗКА: сколько токенов префилла отдавать процессорному исполнителю за раз.\n'
    '    0 (умолчание) = штатный путь: потоковая заливка целых слоёв на карту."""\n'
    "    global _CPU_PREFILL_CHUNK\n"
    "    if _CPU_PREFILL_CHUNK is None:\n"
    "        try:\n"
    '            _CPU_PREFILL_CHUNK = max(0, int(os.environ.get("FT_CPU_PREFILL", "0") or 0))\n'
    "        except ValueError:\n"
    "            _CPU_PREFILL_CHUNK = 0\n"
    "    return _CPU_PREFILL_CHUNK\n"
    "\n"
    "\n"
) + HELPER_BYLO

VETKA_BYLO = (
    '        pass through unmapped."""\n'
    "        cache = self.offload_cache\n"
    "        assert cache is not None\n"
    "        if cache.prefill_overlap:"
)
VETKA_STALO = (
    '        pass through unmapped."""\n'
    "        cache = self.offload_cache\n"
    "        assert cache is not None\n"
    "        _pf = _cpu_prefill_chunk()\n"
    "        if _pf and cache.is_cpu_layer(self.layer_id) and cache.cpu_executor is not None:\n"
    "            # ВРЕЗКА: те же эксперты считает процессор из host banks напрямую.\n"
    "            # Ни один байт весов не идёт через PCIe; position == expert id, как и\n"
    "            # в штатном префилле, поэтому routing ids передаются без правки.\n"
    "            executor = cache.cpu_executor\n"
    '            chunk = min(_pf, int(getattr(executor, "max_tokens", _pf)))\n'
    "            n_tok = hidden_states.shape[0]\n"
    "            if n_tok <= chunk:\n"
    "                return executor.decode(\n"
    "                    self.layer_id, hidden_states, topk_weights, topk_ids\n"
    "                )\n"
    "            parts = []\n"
    "            for i in range(0, n_tok, chunk):\n"
    "                j = min(i + chunk, n_tok)\n"
    "                parts.append(\n"
    "                    executor.decode(\n"
    "                        self.layer_id,\n"
    "                        hidden_states[i:j].contiguous(),\n"
    "                        topk_weights[i:j].contiguous(),\n"
    "                        topk_ids[i:j].contiguous(),\n"
    "                    )\n"
    "                )\n"
    "            return torch.cat(parts, dim=0)\n"
    "        if cache.prefill_overlap:"
)


def podmena(put, bylo, stalo, priznak, imya):
    """Заменить bylo на stalo. priznak — строка, по которой видно, что ЭТА правка
    уже сделана (проверять надо каждую правку отдельно: два куска могут лежать в
    одном файле, и общий признак на файл даёт ложное «уже врезано»)."""
    with open(put, "r", encoding="utf-8") as f:
        t = f.read()
    if priznak in t:
        print("  [%s] уже врезано" % imya)
        return False
    n = t.count(bylo)
    if n != 1:
        sys.exit("  [%s] ОТКАЗ: образец найден %d раз, ожидал 1 — код разошёлся с врезкой" % (imya, n))
    if not os.path.exists(put + BACKUP):
        shutil.copy2(put, put + BACKUP)
    with open(put, "w", encoding="utf-8") as f:
        f.write(t.replace(bylo, stalo))
    print("  [%s] врезано" % imya)
    return True


def otkat(korenj):
    bylo_chto = False
    for otn in ("engine/engine.py", "layers/moe.py"):
        put = os.path.join(korenj, otn)
        if os.path.exists(put + BACKUP):
            shutil.copy2(put + BACKUP, put)
            os.remove(put + BACKUP)
            print("  [%s] восстановлен из бэкапа" % otn)
            bylo_chto = True
        else:
            print("  [%s] бэкапа нет, не трогаю" % otn)
    if not bylo_chto:
        print("откатывать нечего")


def main():
    args = [a for a in sys.argv[1:] if a != "--revert"]
    korenj = args[0] if args else PO_UMOLCHANIYU
    if not os.path.isdir(korenj):
        sys.exit("нет каталога пакета: %s" % korenj)
    engine = os.path.join(korenj, "engine/engine.py")
    moe = os.path.join(korenj, "layers/moe.py")
    for put in (engine, moe):
        if not os.path.exists(put):
            sys.exit("нет файла: %s" % put)

    if "--revert" in sys.argv:
        print("откат врезки в %s" % korenj)
        otkat(korenj)
        return

    print("врезка процессорного префилла в %s" % korenj)
    podmena(engine, ENGINE_BYLO, ENGINE_STALO, "ВРЕЗКА (префилл на процессоре)",
            "engine.py: размер черновиков")
    podmena(moe, HELPER_BYLO, HELPER_STALO, "def _cpu_prefill_chunk",
            "moe.py: чтение FT_CPU_PREFILL")
    podmena(moe, VETKA_BYLO, VETKA_STALO, "_pf = _cpu_prefill_chunk()",
            "moe.py: процессорная ветвь префилла")

    import py_compile
    for put in (engine, moe):
        py_compile.compile(put, doraise=True)
    print("синтаксис обоих файлов проверен")
    print("дальше: export FT_CPU_PREFILL=256 перед запуском ft serve")


if __name__ == "__main__":
    main()
