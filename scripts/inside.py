# -*- coding: utf-8 -*-
"""Второй снимок аквариума — «сквозь стекло».

ЗАЧЕМ. Хозяин заметил верное: там, где стекло вышло глухим, рыбы никуда не
делись — они внутри, их просто не видно. Судить сцену только по внешнему виду
нечестно по отношению к модели: одно дело «рыб не построил», совсем другое
«построил пятнадцать, но спрятал за непрозрачной стенкой». Это разные ошибки и
чинятся по-разному.

КАК. Причина глухого стекла найдена и проверена: сцены приколоты к three.js
r128, где свойство transmission уже объявлено (34 упоминания в сборке), но
механизма отрисовки нет — буфер transmissionRenderTarget появляется только в
r129. Поэтому материал со стеклом рисуется полностью непрозрачным.

Здесь я не правлю сцену, а лишь СМОТРЮ внутрь: перед её запуском подменяю
материал так, чтобы стекло стало обычной полупрозрачностью, которую r128 рисует
прекрасно. Исходный файл не меняется ни на байт — только снимок.

Оба снимка остаются рядом: первый честно показывает, что увидит человек;
второй — что модель на самом деле построила.
"""
import io, json, os, sys
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else "/LLM/hamsters"
ТОЛЬКО = sys.argv[2] if len(sys.argv) > 2 else "Аквариум"
ШИРИНА, ВЫСОТА = 1280, 800
СТРАНИЦЫ = {"index.html", "hamsters.html", "aquarium.html", "minecraft.html", "settings.html"}

# Подменяю материал ДО того, как сцена его создаст. Ловлю два случая: параметры
# переданы в конструктор и свойство присвоено потом.
ПОДМЕНА = """
(() => {
  const СДЕЛАТЬ_ПРОЗРАЧНЫМ = (м) => {
    try { м.transparent = true; м.opacity = Math.min(м.opacity ?? 1, 0.10); м.depthWrite = false; }
    catch (e) {}
  };
  const патч = (T) => {
    if (!T || T.__загляделиВнутрь) return T;
    try {
      for (const имя of ['MeshPhysicalMaterial', 'MeshStandardMaterial']) {
        const исх = T[имя];
        if (!исх) continue;
        // 1. стекло, заданное параметрами конструктора
        const обёртка = function (п) {
          п = п || {};
          if (п.transmission > 0 || п.thickness > 0 || п.ior > 1.0) {
            п.transparent = true;
            п.opacity = Math.min(п.opacity ?? 1, 0.10);
            п.depthWrite = false;
          }
          const м = new исх(п);
          if (п.transmission > 0) СДЕЛАТЬ_ПРОЗРАЧНЫМ(м);
          return м;
        };
        обёртка.prototype = исх.prototype;
        T[имя] = обёртка;
        // 2. стекло, заданное присваиванием уже созданному материалу
        try {
          Object.defineProperty(исх.prototype, 'transmission', {
            configurable: true,
            get() { return this.__прозрачность ?? 0; },
            set(x) { this.__прозрачность = x; if (x > 0) СДЕЛАТЬ_ПРОЗРАЧНЫМ(this); }
          });
        } catch (e) {}
      }
      // Флаг ставлю только если библиотека уже наполнена — иначе пометил бы
      // как обработанную пустышку и больше к ней не вернулся.
      if (T.MeshPhysicalMaterial) T.__загляделиВнутрь = true;
    } catch (e) {}
    return T;
  };
  // ВАЖНО: подменять надо при первом ЧТЕНИИ, а не при присваивании.
  // UMD-сборка three.js делает factory(global.THREE = {}) — то есть сперва
  // кладёт в window.THREE ПУСТОЙ объект и лишь потом наполняет его. Подмена
  // на присваивании видела пустышку и не находила ни одного материала.
  let хранимое;
  Object.defineProperty(window, 'THREE', {
    configurable: true,
    get() { return патч(хранимое); },
    set(v) { хранимое = v; }
  });
})();
"""

задания = []
for группа in sorted(os.listdir(OUT)):
    d = os.path.join(OUT, группа)
    if not os.path.isdir(d) or группа.startswith(".") or ТОЛЬКО not in группа:
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html") or f in СТРАНИЦЫ:
            continue
        html = os.path.join(d, f)
        текст = io.open(html, encoding="utf-8", errors="replace").read()
        if len(текст.strip()) < 500:
            continue
        # Смотрю внутрь только там, где стекло вообще заявлено.
        if "transmission" not in текст:
            continue
        задания.append((группа, f, html))

print("аквариумов со стеклом: %d" % len(задания)); sys.stdout.flush()

сделано = 0
with sync_playwright() as p:
    br = p.chromium.launch(args=["--no-sandbox", "--enable-unsafe-swiftshader",
                                 "--disable-dev-shm-usage"])
    for группа, f, html in задания:
        png = os.path.join(OUT, группа, f[:-5] + "-изнутри.png")
        try:
            стр = br.new_page(viewport={"width": ШИРИНА, "height": ВЫСОТА})
            стр.add_init_script(ПОДМЕНА)
            стр.goto("file://" + html, wait_until="load", timeout=45000)
            try:
                стр.wait_for_function(
                    "() => { const c = document.querySelector('canvas');"
                    " return c && c.width > 50 && c.height > 50; }", timeout=40000)
                готов = True
            except Exception:
                готов = False
            стр.wait_for_timeout(9000 if готов else 15000)
            стр.screenshot(path=png)
            стр.close()
            кб = os.path.getsize(png) / 1024
            print("  %-34s %-26s %6.0f КБ%s"
                  % (группа[:34], f[:26], кб, "" if готов else "  (холст не появился)"))
            сделано += 1
        except Exception as e:
            print("  %-34s %-26s СОРВАЛОСЬ: %s" % (группа[:34], f[:26], str(e)[:70]))
        sys.stdout.flush()
    br.close()
print("снято видов изнутри: %d" % сделано)
