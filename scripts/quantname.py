# -*- coding: utf-8 -*-
"""Какое значение --quantization назвать движку — по КОНФИГУ, а не по имени.

Запускальщик угадывает по имени папки:
    *awq*  -> awq_marlin        *gptq*  -> gptq_marlin
    *fp8*  -> fp8               *quark* -> quark
И промахивается там, где имя говорит одно, а config.json — другое. Так упали
twolven-...-AWQ-MTP и own-...-GPTQ-QTrecipe: в имени AWQ и GPTQ, в конфиге
compressed-tensors. vLLM сверяет и отказывается:
    Quantization method specified in the model config (compressed-tensors)
    does not match the `quantization` argument (awq_marlin)
Здесь беру метод из конфига. Пустая строка = пусть движок определяет сам
(так работали auto-round и модели без кванта в имени).
"""
import json, sys

d = sys.argv[1]
try:
    q = json.load(open(d + "/config.json", encoding="utf-8")).get("quantization_config") or {}
except Exception:
    print("")
    raise SystemExit
метод = (q.get("quant_method") or "").lower()
print({
    "compressed-tensors": "compressed-tensors",
    "awq": "awq_marlin",
    "gptq": "gptq_marlin",
}.get(метод, ""))
