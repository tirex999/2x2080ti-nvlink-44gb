#!/usr/bin/env python3
"""Проверка ответов из eq_gen.py моделью БЕЗ драфтера: ранг каждого выданного токена.

Сервер для проверки — та же модель без спекулятивного декода. Каждый ответ
подаётся ему целиком как промпт (prompt_logprobs), и для каждого токена
смотрится, на каком месте он стоит в распределении модели.

  T=0 — токен обязан быть первым. Второе место с разрывом logprob < 0.5 —
        ничья от округления, не порча.
  T>0 — токен обязан входить в top_k, с которым сэмплировал сервер (у Qwen3.8
        это 20). ВАЖНО: правило верно, только если top_k реально применялся.
        Проверьте в журнале сервера «non-default args»: при
        generation_config='vllm' параметры модели выброшены, сэмплирование
        идёт по всему словарю, и редкие токены с рангом в сотни — норма.

Пример:
  python3 eq_score.py --url http://127.0.0.1:8000 --model qwen38 --tokenizer /path/model --tag spec
"""
import argparse, json, urllib.request
from transformers import AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:8000")
ap.add_argument("--model", required=True)
ap.add_argument("--tokenizer", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--topk", type=int, default=20)
ap.add_argument("--out", default=".")
a = ap.parse_args()

data = json.load(open(f"{a.out}/{a.tag}.json"))
tok = AutoTokenizer.from_pretrained(a.tokenizer)
tot = {}
for r in data:
    P, O = r["prompt_ids"], r["ids"]
    body = {"model": a.model, "prompt": P + O, "max_tokens": 1, "temperature": 0, "prompt_logprobs": a.topk}
    req = urllib.request.Request(a.url + "/v1/completions", json.dumps(body).encode(), {"Content-Type": "application/json"})
    pl = json.load(urllib.request.urlopen(req, timeout=900))["choices"][0]["prompt_logprobs"]
    bad = []
    for j, t in enumerate(O):
        d = pl[len(P) + j] or {}
        e = d.get(str(t)); rank = e["rank"] if e else 10**9
        top = min(d.values(), key=lambda v: v["rank"]) if d else None
        lim = 1 if r["T"] == 0 else a.topk
        if rank > lim:
            gap = (top["logprob"] - e["logprob"]) if (e and top) else None
            bad.append((j, rank, gap, tok.decode([t]), top.get("decoded_token") if top else "?", tok.decode(O[max(0, j - 8):j])))
    big = [b for b in bad if b[2] is None or b[2] > 0.5]
    print(f"T={r['T']} rep={r['rep']} p{r['i']} n={len(O)} нарушений={len(bad)} (разрыв>0.5: {len(big)})")
    for b in big[:4]:
        g = "вне топа" if b[2] is None else f"{b[2]:.3f}"
        print(f"    поз {b[0]} ранг {b[1]} разрыв {g}: {b[3]!r} вместо {b[4]!r} после ...{b[5]!r}")
    x = tot.setdefault(r["T"], [0, 0, 0]); x[0] += len(O); x[1] += len(bad); x[2] += len(big)
for T, (n, v, b) in sorted(tot.items()):
    print(f"ИТОГО T={T}: токенов {n}, нарушений {v}, из них с разрывом >0.5: {b}")
