# 11.10.2026 (tab 180b), Vadim: «прогони вот этот промт на разных уровнях мышления, проверь как он его сделает, все
# косяки и выложи тесты в репо» - the Tidehaven prompt (a Three.js diorama in one index.html) to the live dacan.service
# at the four thinking levels of DACAN's web chat (none / low / medium / high), with the web chat's sampling
# (temperature 0.6, top_p 0.95, top_k 20) and a fixed seed.  Per level: <level>.json (the whole answer + timings),
# <level>.reasoning.txt, <level>.content.md, <level>.index.html (the HTML taken out of the answer).
# BENCH_BASE=http://host:port python3 tidehaven_progon.py <out dir> [levels]   (reads <out dir>/prompt.txt)
# The last line: == ГОТОВО-ПРОГОН
import json
import os
import re
import sys
import time
import urllib.request

URL = os.environ.get("BENCH_BASE", "http://127.0.0.1:8000")   # the OpenAI-compatible server, as bench_ext.py
OUT = sys.argv[1]
LEVELS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["none", "low", "medium", "high"]
PROMPT = open(os.path.join(OUT, "prompt.txt"), encoding="utf-8").read()
SEED = 1110


def get(path):
    return json.load(urllib.request.urlopen(URL + path, timeout=10))


def say(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def html_of(text):
    """The page in the answer: the longest ```html block, else the text from <!DOCTYPE / <html to </html>."""
    blocks = re.findall(r"```(?:html|HTML)?\s*\n(.*?)```", text, re.S)
    blocks = [b for b in blocks if "<html" in b.lower() or "<!doctype" in b.lower()]
    if blocks:
        return max(blocks, key=len)
    m = re.search(r"(<!DOCTYPE html.*?</html>|<html.*?</html>)", text, re.S | re.I)
    return m.group(1) if m else ""


for level in LEVELS:
    for _ in range(720):                       # wait for the service to be free (another chat may be running)
        if not get("/status").get("busy"):
            break
        time.sleep(5)
    body = {"model": "dacan", "stream": False, "messages": [{"role": "user", "content": PROMPT}],
            "reasoning_effort": level, "temperature": 0.6, "top_p": 0.95, "top_k": 20, "seed": SEED}
    say("==", level, "старт")
    t0 = time.time()
    req = urllib.request.Request(URL + "/v1/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        ans = json.load(urllib.request.urlopen(req, timeout=4 * 3600))
    except Exception as e:
        say("==", level, "ОШИБКА", repr(e)[:300])
        continue
    wall = time.time() - t0
    msg = ans["choices"][0]["message"]
    met = {}
    try:
        met = get("/metrics")["requests"][0]
    except Exception:
        pass
    reasoning, content = msg.get("reasoning_content") or "", msg.get("content") or ""
    page = html_of(content)
    rec = {"level": level, "sampling": {k: body[k] for k in ("temperature", "top_p", "top_k", "seed")},
           "wall_s": round(wall, 1), "finish_reason": ans["choices"][0].get("finish_reason"), "usage": ans.get("usage"),
           "metrics": met, "reasoning_chars": len(reasoning), "content_chars": len(content), "html_chars": len(page),
           "model": ans.get("model")}
    with open(os.path.join(OUT, level + ".json"), "w", encoding="utf-8") as f:
        json.dump({**rec, "answer": ans}, f, ensure_ascii=False, indent=1)
    open(os.path.join(OUT, level + ".reasoning.txt"), "w", encoding="utf-8").write(reasoning)
    open(os.path.join(OUT, level + ".content.md"), "w", encoding="utf-8").write(content)
    open(os.path.join(OUT, level + ".index.html"), "w", encoding="utf-8").write(page)
    say("==", level, "готово:", json.dumps({k: rec[k] for k in ("wall_s", "finish_reason", "usage", "reasoning_chars",
                                                                 "content_chars", "html_chars")}, ensure_ascii=False),
        "decode %s tok/s" % met.get("decode_tok_s"))
say("== ГОТОВО-ПРОГОН")
