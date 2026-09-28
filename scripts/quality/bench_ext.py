# -*- coding: utf-8 -*-
"""Прогон эталонных задач (копия bench.py с адресом из BENCH_BASE и контекстом из BENCH_CTX, 26.09.2026).

Одна замерялка на все задачи: список проверок берётся из benchmarks.py, так
что добавить новый эталон стоит одной таблицы, а не нового скрипта.

Потолок ответа считается от контекста в момент запроса — числом его задавать
нельзя, на этом я уже дважды получил ложные провалы.

Аргументы: <ключ-задачи> <прогонов> <подпись-модели> <полное-имя> <квант>
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from benchmarks import BENCHMARKS

# 26.09.2026: адрес движка из окружения (llama-server / Strata на CT 200), по умолчанию как в bench.py
BASE = os.environ.get("BENCH_BASE", "http://127.0.0.1:8000")
OUT = os.environ.get("BENCH_OUT", "gallery")   # у нас /LLM/hamsters
KEY   = sys.argv[1]
RUNS  = int(sys.argv[2])
LABEL = sys.argv[3]
FULL  = sys.argv[4]
QUANT = sys.argv[5]
# Режим размышления: нет | low | medium | xhigh. 'нет' — это enable_thinking
# в шаблоне, а не значение reasoning_effort: шаблон принимает только три
# слова, отключение думания задаётся отдельным ключом.
MODE  = sys.argv[6] if len(sys.argv) > 6 else "medium"
KW = {"enable_thinking": False} if MODE == "нет" else {"reasoning_effort": MODE}
ПОДПИСЬ_РЕЖИМА = {"нет": "без размышления"}.get(MODE, MODE)

B = BENCHMARKS[KEY]
PROMPT = open(B["файл"], encoding="utf-8").read().strip()
CHECKS = B["проверки"]
GROUP = "%s · %s" % (B["название"], LABEL)

d0 = json.load(urllib.request.urlopen(BASE + "/v1/models", timeout=20))
MODEL = d0["data"][0]["id"]
# llama-server/Strata не отдают max_model_len — контекст задаём явно, иначе потолок ответа 30K (ложные провалы)
CTX = int(os.environ.get("BENCH_CTX", "0")) or d0["data"][0].get("max_model_len") or 32768
CAP = max(4096, CTX - 2048)
print("задача: %s | модель: %s | контекст %d | потолок ответа %d"
      % (B["название"], MODEL, CTX, CAP))
print("проверок: %d, порог годности: %d" % (len(CHECKS), B["порог"]))
sys.stdout.flush()


def run(i):
    body = {"model": MODEL, "max_tokens": CAP, "temperature": 0.6,
            "top_p": 0.95, "top_k": 20, "repetition_penalty": 1.05,
            "stream": True, "stream_options": {"include_usage": True},
            "chat_template_kwargs": KW,
            "messages": [{"role": "user", "content": PROMPT}]}
    req = urllib.request.Request(BASE + "/v1/chat/completions",
            json.dumps(body).encode(), {"Content-Type": "application/json"})
    t0 = time.time(); parts, thinks = [], []
    usage = finish = None
    with urllib.request.urlopen(req, timeout=10800) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data: "):
                continue
            p = line[6:]
            if p == "[DONE]":
                break
            try: ev = json.loads(p)
            except ValueError: continue
            if ev.get("usage"): usage = ev["usage"]
            for ch in ev.get("choices", []):
                if ch.get("finish_reason"): finish = ch["finish_reason"]
                dd = ch.get("delta") or {}
                t = dd.get("reasoning_content") or dd.get("reasoning")
                if t: thinks.append(t)
                if dd.get("content"): parts.append(dd["content"])
    dt = time.time() - t0
    content = "".join(parts); think = "".join(thinks)
    n = usage["completion_tokens"] if usage else 0
    blocks = re.findall(r"```(?:html)?\s*(.*?)```", content, re.S)
    code = max(blocks, key=len) if blocks else content
    hits = [nm for nm, pat in CHECKS if re.search(pat, code, re.I)]
    miss = [nm for nm, _ in CHECKS if nm not in hits]
    ok = (finish == "stop") and ("</html>" in code.lower()) and len(hits) >= B["порог"]

    d = os.path.join(OUT, GROUP); os.makedirs(d, exist_ok=True)
    stem = "%s-прогон%d" % (MODE, i)
    open(os.path.join(d, stem + ".html"), "w", encoding="utf-8").write(code)
    open(os.path.join(d, stem + "-размышление.txt"), "w", encoding="utf-8").write(
        think or "(модель не выдала отдельного блока размышления)")
    open(os.path.join(d, stem + "-ответ-целиком.md"), "w", encoding="utf-8").write(content)
    json.dump({"модель": GROUP, "задача": B["название"], "полное_имя": FULL,
               "квант": QUANT, "примечание": B["описание"],
               "контекст": CTX, "потолок_ответа": CAP,
               "подпись": "%s, прогон %d" % (ПОДПИСЬ_РЕЖИМА, i), "прогон": i,
               "режим": ПОДПИСЬ_РЕЖИМА,
               "токенов": n, "секунд": round(dt, 1),
               "токенов_в_секунду": round(n/dt, 1) if dt else 0, "финиш": finish,
               "размышление_символов": len(think), "код_символов": len(code),
               "код_строк": code.count("\n")+1,
               "проверок": len(hits), "всего_проверок": len(CHECKS),
               "порог": B["порог"], "прошло": hits, "не_прошло": miss, "годен": ok},
              open(os.path.join(d, stem + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("  %-16s прогон %d: ток %6d | %7.1f с | %5.1f т/с | %-6s | думал %6d | "
          "код %7d симв %5d строк | %d/%d | %s"
          % (ПОДПИСЬ_РЕЖИМА, i, n, dt, n/dt if dt else 0, finish, len(think), len(code),
             code.count(chr(10))+1, len(hits), len(CHECKS), "ГОДЕН" if ok else "нет"))
    if miss:
        print("     не хватило: %s" % ", ".join(miss[:8]))
    sys.stdout.flush()
    return ok


good = 0
# 28.09.2026: BENCH_START - номер первого прогона (добор прогонов, не затирая прежние), по умолчанию 1
START = int(os.environ.get("BENCH_START", "1"))
for i in range(START, START + RUNS):
    try:
        good += 1 if run(i) else 0
    except Exception as e:
        print("  прогон %d СОРВАЛСЯ: %s" % (i, e)); sys.stdout.flush()
print("ИТОГ %s / %s: годных %d из %d" % (B["название"], LABEL, good, RUNS))
