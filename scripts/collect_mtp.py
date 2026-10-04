# -*- coding: utf-8 -*-
"""Достаю из журнала сервера все окна замера в таблицу.
Каждая строка — одно десятисекундное окно: скорость, приёмка, длина принятого,
темп черновика, приёмка по позициям. Это сырьё, из которого считались выводы;
выкладываю его целиком, чтобы каждый мог пересчитать сам."""
import re, glob, io, os, sys
L = max(glob.glob("/root/vllm-0.2.x/run-logs/vllm-qwen38awq-*.log"), key=os.path.getmtime)
out = ["# Замер vLLM 0.2.1-pre3 / Qwen3.8-27B AWQ-MTP / 2x RTX 2080Ti 22GB + NVLink",
       "# MTP_K=4, MAX_NUM_SEQS=1, TP=2, KV fp16, контекст 131072",
       "# Источник: строки loggers.py:310 и metrics.py:120 журнала сервера, окно 10 с.",
       "# Время UTC. Пустая приёмка = окно без спекулятивной статистики.",
       "utc\tgen_tps\tprompt_tps\trunning\tkv_pct\tprefix_hit_pct\tacc_len\tacc_rate_pct\tdrafted_tps\taccepted_tps\tpos1\tpos2\tpos3\tpos4"]
cur = None
n = 0
for line in io.open(L, encoding="utf-8", errors="replace"):
    m = re.search(r"INFO (\d\d-\d\d \d\d:\d\d:\d\d).*Avg prompt throughput: ([\d.]+) tokens/s, "
                  r"Avg generation throughput: ([\d.]+) tokens/s, Running: (\d+) reqs, "
                  r"Waiting: \d+ reqs, GPU KV cache usage: ([\d.]+)%, Prefix cache hit rate: ([\d.]+)%", line)
    if m:
        if cur:
            out.append(cur + "\t\t\t\t\t\t\t\t")
        cur = "%s\t%s\t%s\t%s\t%s\t%s" % (m.group(1), m.group(3), m.group(2),
                                          m.group(4), m.group(5), m.group(6))
        continue
    m = re.search(r"Mean acceptance length: ([\d.]+), Accepted throughput: ([\d.]+) tokens/s, "
                  r"Drafted throughput: ([\d.]+) tokens/s.*Per-position acceptance rate: "
                  r"([\d.]+), ([\d.]+), ([\d.]+), ([\d.]+), Avg Draft acceptance rate: ([\d.]+)%", line)
    if m and cur:
        out.append("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                   (cur, m.group(1), m.group(8), m.group(3), m.group(2),
                    m.group(4), m.group(5), m.group(6), m.group(7)))
        cur = None
        n += 1
if cur:
    out.append(cur + "\t\t\t\t\t\t\t\t")
sys.stdout.write("\n".join(out) + "\n")
sys.stderr.write("окон со спекулятивной статистикой: %d, всего строк: %d\n" % (n, len(out) - 5))
