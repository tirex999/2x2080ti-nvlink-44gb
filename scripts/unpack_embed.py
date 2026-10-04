# -*- coding: utf-8 -*-
"""Лечение шестибитной сборки: развернуть эмбеддинги и выходной слой.

БОЛЕЗНЬ (замер, не догадка). vLLM отказывается поднимать модель:
    ValueError: There is no module or parameter named 'embed_tokens.weight_packed'
    in Qwen3_5Model. The available parameters are: {'embed_tokens.weight'}
Причина в конфиге кванта: группа group_2 нацелена на re:.*embed_tokens и
re:.*lm_head. Автор пожал восемью битами не только линейные слои, но и таблицу
слов с выходным слоем. Слой VocabParallelEmbedding в vLLM сжатый формат не
принимает — он ждёт обычный .weight.

ЛЕЧЕНИЕ. Развернуть ровно эти два тензора обратно в bf16 и вычеркнуть их из
описания кванта. Линейные слои остаются шестибитными — ради них всё и делается.
Цена: около пяти гигабайт веса (два тензора 248320×5120 в bf16 вместо упакованных).

ЧТО НЕ ДЕЛАЮ. Не трогаю исходную папку: собираю новую. Сравнение «было/стало»
должно оставаться возможным.
"""
import io, json, os, shutil, sys
import torch
from safetensors import safe_open
from safetensors.torch import save_file
from compressed_tensors.compressors.pack_quantized.helpers import unpack_from_int32

СТАРАЯ = "/LLM/models/vllm-ready/Minachist-Qwen3.8-27B-INT6-Flat-6.6bpw-AutoRound"
НОВАЯ = "/LLM/models/vllm-ready/own-Qwen3.8-27B-INT6-embed-bf16"
# Что разворачиваем: сжатое имя -> имя, которое ждёт vLLM.
РАЗВЕРНУТЬ = {
    "model.language_model.embed_tokens": "model.language_model.embed_tokens.weight",
    "lm_head": "lm_head.weight",
}
БИТ = 8          # group_2 в конфиге: num_bits 8 для эмбеддингов и выходного слоя

os.makedirs(НОВАЯ, exist_ok=True)
индекс = json.load(io.open(os.path.join(СТАРАЯ, "model.safetensors.index.json"),
                           encoding="utf-8"))
карта = индекс["weight_map"]

# Какие шарды придётся переписать, а какие можно просто связать жёсткой ссылкой.
трогаем = {}
for префикс in РАЗВЕРНУТЬ:
    ключ = префикс + ".weight_packed"
    if ключ not in карта:
        sys.exit("нет ключа %s — модель устроена иначе, разбираться руками" % ключ)
    трогаем.setdefault(карта[ключ], []).append(префикс)
print("переписываю шардов: %d (%s)" % (len(трогаем), ", ".join(sorted(трогаем))))

# 1. Всё, что не трогаем, — переносим как есть.
for имя in sorted(os.listdir(СТАРАЯ)):
    путь = os.path.join(СТАРАЯ, имя)
    if not os.path.isfile(путь) or имя in трогаем:
        continue
    цель = os.path.join(НОВАЯ, имя)
    if os.path.exists(цель):
        continue
    try:
        os.link(путь, цель)               # без копирования, если файловая система даст
    except OSError:
        shutil.copy2(путь, цель)
print("перенесено файлов без изменений: %d" % len(os.listdir(НОВАЯ)))

# 2. Переписываем нужные шарды.
новые_ключи, убранные_ключи = [], []
for шард, префиксы in sorted(трогаем.items()):
    print("  шард %s: разворачиваю %s" % (шард, ", ".join(префиксы)))
    тензоры = {}
    with safe_open(os.path.join(СТАРАЯ, шард), framework="pt") as s:
        имена = list(s.keys())
        for k in имена:
            тензоры[k] = s.get_tensor(k)

    for префикс in префиксы:
        упак = тензоры.pop(префикс + ".weight_packed")
        масштаб = тензоры.pop(префикс + ".weight_scale")
        форма = тензоры.pop(префикс + ".weight_shape")
        убранные_ключи += [префикс + ".weight_packed", префикс + ".weight_scale",
                           префикс + ".weight_shape"]

        строк, столбцов = int(форма[0]), int(форма[1])
        целые = unpack_from_int32(упак, БИТ, torch.Size([строк, столбцов]))
        # Симметричное квантование: нуля-смещения нет, только масштаб по группам.
        размер_группы = столбцов // масштаб.shape[1]
        assert размер_группы * масштаб.shape[1] == столбцов, "масштаб не делит строку нацело"
        вес = (целые.to(torch.float32) *
               масштаб.to(torch.float32).repeat_interleave(размер_группы, dim=1))
        вес = вес.to(torch.bfloat16).contiguous()

        имя_нового = РАЗВЕРНУТЬ[префикс]
        тензоры[имя_нового] = вес
        новые_ключи.append((имя_нового, шард))
        print("     %s: %s x %s, группа %d -> %s %s, %.2f ГБ"
              % (префикс, строк, столбцов, размер_группы,
                 tuple(вес.shape), вес.dtype, вес.numel() * 2 / 1073741824))
        del упак, масштаб, целые
    save_file(тензоры, os.path.join(НОВАЯ, шард), metadata={"format": "pt"})
    del тензоры

# 3. Указатель на веса.
for k in убранные_ключи:
    карта.pop(k, None)
for имя, шард in новые_ключи:
    карта[имя] = шард
общий = sum(os.path.getsize(os.path.join(НОВАЯ, f))
            for f in os.listdir(НОВАЯ) if f.endswith(".safetensors"))
индекс["metadata"] = {"total_size": общий}
json.dump(индекс, io.open(os.path.join(НОВАЯ, "model.safetensors.index.json"),
                          "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("указатель обновлён: ключей %d, общий вес %.1f ГБ"
      % (len(карта), общий / 1073741824))

# 4. Конфиг: вычёркиваем группу, которая жала эмбеддинги.
конф = json.load(io.open(os.path.join(СТАРАЯ, "config.json"), encoding="utf-8"))
q = конф.get("quantization_config") or {}
группы = q.get("config_groups") or {}
выкинуть = [имя for имя, гр in группы.items()
            if any("embed_tokens" in t or "lm_head" in t for t in (гр.get("targets") or []))]
for имя in выкинуть:
    print("  убираю группу %s (жала эмбеддинги и выходной слой)" % имя)
    группы.pop(имя)
q["ignore"] = sorted(set((q.get("ignore") or []) +
                         ["re:.*embed_tokens", "re:.*lm_head"]))
json.dump(конф, io.open(os.path.join(НОВАЯ, "config.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("конфиг переписан: групп осталось %d, в списке исключений %d записей"
      % (len(группы), len(q["ignore"])))
print("ГОТОВО:", НОВАЯ)
