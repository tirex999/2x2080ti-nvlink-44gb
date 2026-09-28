# -*- coding: utf-8 -*-
# 28.09.2026: префилл Strata на всём контексте + проверка, что модель видит весь контекст (иголка в стоге).
# Стог - исходники vLLM (английский код), в каждом запросе своё начало (кэш разговора не подхватит прошлый),
# кодовое слово спрятано на 40 % глубины. Запрос как боевой: без max_tokens, выборка службы, размышление включено.
# Скорость префилла - prompt_ms из /metrics службы (чтение промпта отдельно от ответа).
import glob, json, os, sys, time, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
SIZES = [8000, 32000, 128000, 240000]
WORDS = ["ФИОЛЕТОВЫЙ-ДИРИЖАБЛЬ-7342", "ЖЕЛЕЗНЫЙ-ПЕЛИКАН-5190", "ТИХИЙ-КАШАЛОТ-2861", "ЛУННЫЙ-ТРАКТОР-9057"]
OUT = os.environ.get("NEEDLE_OUT", "needle.json")
CORPUS = os.environ.get("NEEDLE_CORPUS", "/root/vllm-0.2.x")   # любой большой каталог *.py; у нас исходники vLLM

files = sorted(glob.glob(CORPUS + "/**/*.py", recursive=True))
corpus = []
total = 0
for f in files:
    try:
        t = open(f, encoding="utf-8").read()
    except Exception:
        continue
    corpus.append("# file: %s\n%s\n" % (os.path.relpath(f, CORPUS), t))
    total += len(corpus[-1])
    if total > 2_600_000:
        break
corpus = "".join(corpus)
print("стог: %d файлов, %d знаков" % (len(files), len(corpus)))
MODEL = json.load(urllib.request.urlopen(BASE + "/v1/models", timeout=20))["data"][0]["id"]


def metrics_last():
    h = json.load(urllib.request.urlopen(BASE + "/metrics", timeout=20)).get("requests") or []
    return h[0] if h else {}


ratio = 3.3   # знаков на токен, уточняется по первому ответу
results = []
for i, size in enumerate(SIZES):
    n = int(size * ratio)
    start = (i * 400_000) % max(1, len(corpus) - n) if len(corpus) > n else 0
    text = corpus[start:start + n]
    cut = int(len(text) * 0.4)
    cut = text.rfind("\n", 0, cut) + 1 or cut
    word = WORDS[i % len(WORDS)]
    text = (text[:cut] + "\n# ВАЖНО: кодовое слово для проверки - %s. Запомни его.\n" % word + text[cut:])
    prompt = ("Документ %d (исходный код, фрагмент %d).\n\n%s\n\nКонец документа. Где-то в документе выше спрятано "
              "кодовое слово для проверки. Назови его." % (i + 1, start, text))
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    t0 = time.time()
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            BASE + "/v1/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=7200))
    except Exception as e:
        print("== %dK: ОШИБКА %s" % (size // 1000, e)); sys.stdout.flush()
        results.append({"цель_токенов": size, "ошибка": str(e)})
        continue
    dt = time.time() - t0
    m = metrics_last()
    u = r.get("usage") or {}
    msg = r["choices"][0]["message"]
    ans = (msg.get("content") or "").strip()
    pt = u.get("prompt_tokens") or m.get("prompt_tokens") or 0
    if i == 0 and pt:
        ratio = len(prompt) / pt
    pms = m.get("prompt_ms") or 0
    row = {"цель_токенов": size, "промпт_токенов": pt, "подхвачено_из_кэша": m.get("reused"),
           "префилл_мс": pms, "префилл_т_с": round((pt - (m.get("reused") or 0)) / (pms / 1000), 1) if pms else None,
           "ответ_токенов": u.get("completion_tokens"), "декод_т_с": m.get("decode_tok_s"),
           "всего_с": round(dt, 1), "финиш": r["choices"][0].get("finish_reason"),
           "кодовое_слово": word, "нашла": word in ans.upper().replace(" ", ""), "ответ": ans[:300],
           "размышление_знаков": len(msg.get("reasoning_content") or "")}
    results.append(row)
    print("== %s" % json.dumps(row, ensure_ascii=False)); sys.stdout.flush()
    json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ГОТОВО")
