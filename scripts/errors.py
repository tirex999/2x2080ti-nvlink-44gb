# -*- coding: utf-8 -*-
"""Собирает улики со сцен, НЕ трогая снимки.

Зачем отдельно от съёмки. Снимки уже сделаны и уже разбираются глазами; если
переснять их заново, разбор будет про другие кадры — сцены живые, каждый кадр
свой. Поэтому здесь только открываю страницу, слушаю ошибки JavaScript и кладу
их рядом со снимком. Картинку не перезаписываю.

Ошибка страницы — объективный признак негодной сцены, и зрение для неё не
нужно: шестнадцать битых сцен из девяноста шести нашлись именно так.
"""
import io, json, os, re, sys
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else "/LLM/hamsters"
ОСЕСТЬ_МС = 6000
ШИРИНА, ВЫСОТА = 1280, 800
СТРАНИЦЫ_САЙТА = {"index.html", "hamsters.html", "aquarium.html",
                  "minecraft.html", "settings.html"}

задания = []
for группа in sorted(os.listdir(OUT)):
    d = os.path.join(OUT, группа)
    if not os.path.isdir(d) or группа.startswith("."):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html") or f in СТРАНИЦЫ_САЙТА:
            continue
        html = os.path.join(d, f)
        текст = io.open(html, encoding="utf-8", errors="replace").read()
        if len(текст.strip()) < 500 or "</html>" not in текст.lower():
            continue
        задания.append((группа, f, html))

print("сцен к осмотру: %d" % len(задания)); sys.stdout.flush()

падают = 0
with sync_playwright() as p:
    br = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader",
                                 "--disable-dev-shm-usage"])
    for группа, f, html in задания:
        ошибки = []
        готов = False
        try:
            стр = br.new_page(viewport={"width": ШИРИНА, "height": ВЫСОТА})
            стр.on("pageerror", lambda e: ошибки.append(str(e)[:160]))
            стр.goto("file://" + html, wait_until="load", timeout=45000)
            try:
                стр.wait_for_function(
                    "() => { const c = document.querySelector('canvas');"
                    " return c && c.width > 50 && c.height > 50; }",
                    timeout=40000)
                готов = True
            except Exception:
                готов = False
            стр.wait_for_timeout(ОСЕСТЬ_МС if готов else 12000)
            try:
                видно = стр.inner_text("body")[:3000]
            except Exception:
                видно = ""
            if re.search("click to play|press to start|нажмите|кликните|начать",
                         видно, re.I):
                try:
                    стр.mouse.click(ШИРИНА // 2, ВЫСОТА // 2)
                    стр.wait_for_timeout(4000)
                except Exception:
                    pass
            стр.close()
        except Exception as e:
            ошибки.append("не открылась: " + str(e)[:120])

        json.dump({"ошибки_страницы": ошибки, "холст_появился": готов},
                  io.open(os.path.join(OUT, группа, f[:-5] + "-осмотр.json"),
                          "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if ошибки or not готов:
            падают += 1
            print("  %-34s %-26s %s" % (группа[:34], f[:26],
                  (ошибки[0][:70] if ошибки else "холст не появился")))
            sys.stdout.flush()

print("ИТОГ: осмотрено %d, с бедой %d" % (len(задания), падают))
