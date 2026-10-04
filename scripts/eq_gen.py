#!/usr/bin/env python3
"""Генерация контрольных ответов со спекулятивным декодом — вход для eq_score.py.

Зачем. Скорость спекулятивного декода легко принять за победу, не заметив, что
текст испорчен: склейки слов («лежитжат»), обрывы посреди размышления. Глазом
это ловится не всегда. Поэтому ответы сохраняются вместе с id токенов, а потом
каждый токен проверяется моделью БЕЗ драфтера (eq_score.py).

Пример:
  python3 eq_gen.py --url http://127.0.0.1:8000 --model qwen38 --tag spec --temps 0,1 --reps 2
"""
import argparse, json, time, urllib.request

PROMPTS = [
    "Расскажи подробно, как работает двигатель внутреннего сгорания. Пиши по-русски, 3 абзаца.",
    "Напиши на Python функцию быстрой сортировки с комментариями и пример запуска.",
    "Реши задачу: в корзине 17 яблок, трое детей берут по 4, потом кладут обратно 5. Сколько осталось? Объясни по шагам.",
    "Составь список из 12 столиц Европы с одной интересной деталью о каждой.",
]

ap = argparse.ArgumentParser()
ap.add_argument("--url", default="http://127.0.0.1:8000")
ap.add_argument("--model", required=True)
ap.add_argument("--tag", required=True, help="имя прогона, файл <out>/<tag>.json")
ap.add_argument("--temps", default="0,1")
ap.add_argument("--reps", type=int, default=1)
ap.add_argument("--max-tokens", type=int, default=1500)
ap.add_argument("--out", default=".")
a = ap.parse_args()

out = []
for T in [float(t) for t in a.temps.split(",")]:
    for rep in range(a.reps):
        for i, p in enumerate(PROMPTS):
            body = {"model": a.model, "messages": [{"role": "user", "content": p}], "temperature": T,
                    "max_tokens": a.max_tokens, "return_token_ids": True, "seed": 1000 + rep}
            req = urllib.request.Request(a.url + "/v1/chat/completions", json.dumps(body).encode(),
                                         {"Content-Type": "application/json"})
            s = time.time(); r = json.load(urllib.request.urlopen(req, timeout=900)); d = time.time() - s
            ch = r["choices"][0]; m = ch["message"]
            content = m.get("content") or ""
            out.append({"T": T, "rep": rep, "i": i, "prompt_ids": r.get("prompt_token_ids"), "ids": ch.get("token_ids"),
                        "text": (m.get("reasoning") or "") + "\n<<CONTENT>>\n" + content,
                        "n": r["usage"]["completion_tokens"], "sec": d, "finish": ch["finish_reason"]})
            empty = " ПУСТОЙ ОТВЕТ" if ch["finish_reason"] == "stop" and not content.strip() else ""
            print(f"{a.tag} T={T} rep={rep} p{i} tokens={out[-1]['n']} t/s={out[-1]['n']/d:.1f} "
                  f"finish={ch['finish_reason']}{empty}", flush=True)
json.dump(out, open(f"{a.out}/{a.tag}.json", "w"), ensure_ascii=False)
for T in sorted({x["T"] for x in out}):
    xs = [x for x in out if x["T"] == T]; n = sum(x["n"] for x in xs); s = sum(x["sec"] for x in xs)
    print(f"СВОДКА T={T}: {n} токенов за {s:.1f} с = {n/s:.1f} т/с")
