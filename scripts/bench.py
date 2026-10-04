#!/usr/bin/env python3
"""Честный замер скорости llama-server.

ЗАЧЕМ ИМЕННО ТАК. У сервера ДВЕ разные скорости, и мерить надо обе:

    prompt_per_second     обработка промпта  — упирается в вычисления
    predicted_per_second  генерация          — упирается в память

Замерив одну, легко принять регрессию за улучшение: например, урезав число
потоков, можно поднять генерацию на 3% и одновременно обвалить обработку
промпта — и не заметить этого, пока не пожалуется человек.

Обе цифры берутся из поля timings ответа сервера, а не секундомером снаружи:
секундомер меряет ещё и сеть, и разбор JSON.

Greedy и обязательный прогрев. При temperature 0.6 разброс достигает
20 пунктов на одинаковых промптах — такие цифры не воспроизводятся.
Первый запрос после старта всегда медленнее, это прогрев, а не конфигурация.
"""
import json
import urllib.request

URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "qwen38-next"

# Длинный промпт нужен, чтобы обработка промпта была видна отдельно от
# генерации: на коротком её вклад теряется в шуме.
LONG = ("Рынок движется уровнями, и алгоритм биржи расставляет их заранее. " * 120).strip()


def ask(text, max_tokens):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": text}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        URL, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=1800).read())


def main():
    ask("прогрев", 8)
    for run in range(1, 4):
        t = ask(LONG, 256).get("timings", {})
        print("прогон %d: промпт %d токенов %.1f т/с | генерация %d токенов %.1f т/с" % (
            run,
            t.get("prompt_n", 0), t.get("prompt_per_second", 0.0),
            t.get("predicted_n", 0), t.get("predicted_per_second", 0.0),
        ))


if __name__ == "__main__":
    main()
