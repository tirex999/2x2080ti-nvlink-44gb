# -*- coding: utf-8 -*-
# 11.10.2026: the Tidehaven task (scripts/quality/prompts/tidehaven_prompt.txt) checked in a real browser, the way the
# prompt itself asks: "Test every button, camera, audio control, water transparency, and the mobile layout".
# Headless Chromium (Playwright) with software WebGL (SwiftShader), one page at a time:
#   load        - the page's own errors (console + uncaught), the WebGL canvas, a picture that is not one colour,
#                 the scene moving (two frames 1.5 s apart differ);
#   audio       - no AudioContext before the first click (the prompt: audio only after a user interaction), one after
#                 the music button, and its state;
#   controls    - every button clicked in turn and every slider moved to both ends: errors after it, did the picture
#                 change, a screenshot of each;
#   pause       - with "Pause" on, two frames 1.5 s apart are the same;
#   resize      - the canvas follows the window; pixel ratio capped (a 3x screen draws at most 2x);
#   mobile      - 390x844 at 3x: no sideways scroll, a way to collapse the panels, a screenshot;
#   static      - what the prompt names in the code: Three.js from a CDN, OrbitControls, InstancedMesh, delta time,
#                 Web Audio, setPixelRatio capped, resize handler, no external models.
# Output: <out>/<name>/report.json (verdicts, the list of problems) and the screenshots.
#   python tidehaven_test.py <page.html> <out dir> [name]
import hashlib
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

PAGE, OUT = sys.argv[1], sys.argv[2]
NAME = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(os.path.basename(PAGE))[0]
DIR = os.path.join(OUT, NAME)
os.makedirs(DIR, exist_ok=True)
CODE = open(PAGE, encoding="utf-8", errors="replace").read()
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"]

# counts every AudioContext the page makes and when (before or after the first click)
AUDIO_HOOK = """
(() => {
  window.__ac = {made: 0, before_click: 0, clicked: false, states: []};
  addEventListener('pointerdown', () => { window.__ac.clicked = true; }, true);
  addEventListener('click', () => { window.__ac.clicked = true; }, true);
  for (const k of ['AudioContext', 'webkitAudioContext']) {
    const C = window[k];
    if (!C) continue;
    window[k] = class extends C {
      constructor(...a) { super(...a); window.__ac.made++; if (!window.__ac.clicked) window.__ac.before_click++;
                          window.__ac.states.push(this); }
    };
  }
})();
"""

report = {"страница": NAME, "размер_кода": len(CODE), "проверки": {}, "косяки": [], "кнопки": [], "ползунки": []}


def check(key, ok, note=""):
    report["проверки"][key] = {"ok": bool(ok), "заметка": note}
    if not ok:
        report["косяки"].append(f"{key}: {note}" if note else key)


SHOT_TIMEOUT = 120000   # a heavy scene in software WebGL takes tens of seconds per frame


def shot(page, name):
    path = os.path.join(DIR, name + ".png")
    try:
        page.screenshot(path=path, timeout=SHOT_TIMEOUT)
    except Exception as e:
        report.setdefault("снимки_не_сняты", []).append(f"{name}: {str(e).splitlines()[0][:100]}")
        return None
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def canvas_shot(page):
    """md5 of the canvas area only (the panels with their animated numbers left out)."""
    c = page.query_selector("canvas")
    if not c:
        return None
    try:
        return hashlib.md5(c.screenshot(timeout=SHOT_TIMEOUT)).hexdigest()
    except Exception:
        return None


def canvas_png(page):
    c = page.query_selector("canvas")
    try:
        return c.screenshot(timeout=SHOT_TIMEOUT) if c else None
    except Exception:
        return None


def changed_share(a, b):
    """Share of canvas pixels that changed by more than 8 levels between two screenshots."""
    import io
    from PIL import Image, ImageChops
    if a is None or b is None:
        return 0.0
    d = ImageChops.difference(Image.open(io.BytesIO(a)).convert("L"), Image.open(io.BytesIO(b)).convert("L"))
    hist = d.histogram()
    return sum(hist[9:]) / max(1, sum(hist))


def canvas_spread(page):
    """Brightness spread of the canvas as drawn (a screenshot: reading a WebGL canvas back needs preserveDrawingBuffer)."""
    c = page.query_selector("canvas")
    if not c:
        return 0.0
    import io
    from PIL import Image, ImageStat
    im = Image.open(io.BytesIO(c.screenshot(timeout=SHOT_TIMEOUT))).convert("L")
    return ImageStat.Stat(im).stddev[0]


ENTER = re.compile(r"^\W*(enter|start|begin|explore|dive in|let'?s go)\b", re.I)


def on_top(page, el):
    """The element is what a click at its centre hits (not covered by an overlay)."""
    return page.evaluate("""el => { const r = el.getBoundingClientRect(); if (!r.width) return false;
        const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
        return !!t && (t === el || el.contains(t)); }""", el)


def press(b):
    """A click as a visitor makes it; a button that keeps animating (a pulsing «Step ashore») never counts as
    «stable» for Playwright, so after 5 s it is clicked without that wait."""
    try:
        b.click(timeout=5000)
    except Exception:
        b.click(timeout=5000, force=True)


def enter(page, report, wait_s=90):
    """A start screen ("Enter the diorama") in front of the controls: pressed once, as a visitor would.  A page that
    is still loading gets up to wait_s for its button to appear (software WebGL builds a big scene slowly); a page
    without a start screen is left as it is once no overlay covers its controls."""
    t0 = time.time()
    while time.time() - t0 < wait_s:
        # by what it does, not by its word ("Step ashore", "Enter the diorama"): when the page's buttons are covered
        # and only one or two can be reached, those are the way in
        vis = [x for x in page.query_selector_all("button, a, [role=button]") if x.is_visible()]
        top = [x for x in vis if on_top(page, x)]
        if top and len(top) <= 2 and len(vis) - len(top) >= 3:
            b = next((x for x in top if ENTER.search(label_of(page, x))), top[0])
            t = label_of(page, b)
            press(b)
            page.wait_for_timeout(5000)
            report.setdefault("заставка", t)
            report.setdefault("заставка_через_с", round(time.time() - t0, 1))
            return t
        for b in vis:
            if ENTER.search(label_of(page, b)) and on_top(page, b):
                t = label_of(page, b)
                press(b)
                page.wait_for_timeout(5000)
                report.setdefault("заставка", t)
                report.setdefault("заставка_через_с", round(time.time() - t0, 1))
                return t
        ctrls = [b for b in page.query_selector_all("button") if b.is_visible()]
        if ctrls and any(on_top(page, b) for b in ctrls) and not any(ENTER.search(label_of(page, b)) for b in ctrls):
            return None                          # no start screen: the controls are reachable
        page.wait_for_timeout(2000)
    report.setdefault("заставка", f"не дождался кнопки входа и доступных кнопок за {wait_s} с")
    return None


def label_of(page, el):
    return (el.inner_text() or el.get_attribute("aria-label") or el.get_attribute("title") or
            el.get_attribute("id") or "").strip().replace("\n", " ")[:40]


# ---- static: what the prompt names, in the code
st = {
    "three.js с CDN": re.search(r"(unpkg\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|esm\.sh|skypack)[^\"']*three", CODE, re.I),
    "OrbitControls": re.search(r"OrbitControls", CODE),
    "InstancedMesh": re.search(r"InstancedMesh", CODE),
    "время кадра (delta)": re.search(r"getDelta\(\)|\bdelta\b|\bdt\b", CODE),
    "Web Audio": re.search(r"AudioContext", CODE),
    "предел pixel ratio": re.search(r"setPixelRatio\s*\(\s*Math\.min", CODE),
    "обработчик resize": re.search(r"addEventListener\(\s*['\"]resize", CODE),
    "без внешних моделей": not re.search(r"GLTFLoader|OBJLoader|FBXLoader|\.glb['\"]|\.gltf['\"]", CODE),
    "тени": re.search(r"shadowMap\.enabled\s*=\s*true", CODE),
    "закрывается </html>": "</html>" in CODE.lower(),
}
for k, v in st.items():
    check("код: " + k, v)

errors = []
with sync_playwright() as pw:
    br = pw.chromium.launch(args=ARGS)
    # ---- desktop
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    ctx.add_init_script(AUDIO_HOOK)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(("console", m.text)) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(("page", str(e))))
    t0 = time.time()
    page.goto("file:///" + os.path.abspath(PAGE).replace("\\", "/"), wait_until="load", timeout=120000)
    page.wait_for_timeout(6000)
    report["загрузка_с"] = round(time.time() - t0, 1)
    n_err_load = len(errors)
    check("загрузка без ошибок", n_err_load == 0, "; ".join(e[1][:160] for e in errors[:5]))
    has_canvas = page.evaluate("() => { const c = document.querySelector('canvas'); if (!c) return 0;"
                               " const g = c.getContext('webgl2') || c.getContext('webgl'); return g ? 2 : 1; }")
    check("холст WebGL", has_canvas == 2, "нет холста" if has_canvas == 0 else ("холст без WebGL" if has_canvas == 1 else ""))
    h1 = shot(page, "01-старт")
    ac = page.evaluate("() => ({made: window.__ac.made, before: window.__ac.before_click})")
    check("звук не до клика", ac["before"] == 0, f"AudioContext создан до клика: {ac['before']}")
    if enter(page, report):
        shot(page, "02-после-заставки")
    var = canvas_spread(page)
    check("сцена нарисована (не один цвет)", var > 8, f"разброс яркости {var:.1f}")
    a, _ = canvas_shot(page), page.wait_for_timeout(1500)
    b = canvas_shot(page)
    check("сцена движется", a != b, "два кадра через 1.5 с одинаковые" if a == b else "")

    # ---- every button and slider
    buttons = [b for b in page.query_selector_all("button") if b.is_visible()]
    covered = [label_of(page, b) for b in buttons if not on_top(page, b)]
    if covered:
        report["перекрытые_кнопки"] = covered
    report["кнопок_видно"] = len(buttons)
    pause_btn = None
    for i, btn in enumerate(buttons):
        name = label_of(page, btn)
        if re.search(r"pause", name, re.I) and pause_btn is None:
            pause_btn = btn
        e0 = len(errors)
        before = canvas_shot(page)
        cls0 = (btn.get_attribute("class") or "") + "|" + (btn.get_attribute("aria-pressed") or "") + "|" + name
        try:
            btn.click(timeout=5000)
        except Exception as e:
            report["кнопки"].append({"кнопка": name, "нажалась": False, "ошибка": str(e)[:120]})
            report["косяки"].append(f"кнопка «{name}» не нажимается")
            continue
        page.wait_for_timeout(2500)
        after = canvas_shot(page)
        shot(page, f"кн-{i:02d}-" + re.sub(r"[^\w-]+", "_", name)[:30])
        new_err = [x[1][:160] for x in errors[e0:]]
        cls1 = (btn.get_attribute("class") or "") + "|" + (btn.get_attribute("aria-pressed") or "") + "|" + label_of(page, btn)
        report["кнопки"].append({"кнопка": name, "нажалась": True, "картинка_изменилась": before != after,
                                 "вид_кнопки_изменился": cls0 != cls1, "ошибки": new_err})
        if new_err:
            report["косяки"].append(f"кнопка «{name}»: ошибки {new_err[:2]}")
    ac = page.evaluate("() => ({made: window.__ac.made, before: window.__ac.before_click,"
                       " states: window.__ac.states.map(c => c.state)})")
    report["звук"] = ac
    check("звук включается кнопкой", ac["made"] >= 1 and "running" in ac["states"],
          f"AudioContext: {ac['made']}, состояния {ac['states']}")

    sliders = page.query_selector_all("input[type=range]")
    for s in sliders:
        lab = page.evaluate("""el => { const l = el.id && document.querySelector(`label[for="${el.id}"]`);
            return (l && l.innerText) || el.getAttribute('aria-label') || el.name || el.id ||
                   (el.parentElement && el.parentElement.innerText) || ''; }""", s).strip().replace("\n", " ")[:40]
        e0 = len(errors)
        res = {"ползунок": lab}
        for end in ("min", "max"):
            before = canvas_shot(page)
            page.evaluate("""([el, end]) => { el.value = el[end] || (end === 'min' ? 0 : 100);
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true})); }""", [s, end])
            page.wait_for_timeout(3000)
            res[end + "_картинка_изменилась"] = before != canvas_shot(page)
            shot(page, "пол-" + re.sub(r"[^\w-]+", "_", lab)[:24] + "-" + end)
        res["ошибки"] = [x[1][:160] for x in errors[e0:]]
        report["ползунки"].append(res)
        if res["ошибки"]:
            report["косяки"].append(f"ползунок «{lab}»: ошибки {res['ошибки'][:2]}")

    # ---- pause: the world stops
    try:
        if pause_btn is not None:
            txt = label_of(page, pause_btn)
            if re.search(r"resume|play", txt, re.I):        # left paused by the button pass: start it first
                pause_btn.click(); page.wait_for_timeout(1000)
            pause_btn.click(); page.wait_for_timeout(1500)
            a = canvas_png(page); page.wait_for_timeout(1500); b = canvas_png(page)
            sh = changed_share(a, b)
            report["пауза_доля_пикселей"] = round(sh, 4)
            check("пауза останавливает мир", sh < 0.005, f"при паузе за 1.5 с изменилось {sh * 100:.1f} % пикселей")
            shot(page, "пауза")
            pause_btn.click(); page.wait_for_timeout(1500)
            a = canvas_png(page); page.wait_for_timeout(1500); b = canvas_png(page)
            sh2 = changed_share(a, b)
            check("после паузы мир идёт", sh2 > sh, f"изменилось {sh2 * 100:.1f} % пикселей")
        else:
            check("пауза останавливает мир", False, "кнопка Pause не найдена")
            check("после паузы мир идёт", False, "кнопка Pause не найдена")
    except Exception as e:
        why = "кнопка Pause не нажимается: " + str(e).split(chr(10))[0][:100]
        check("пауза останавливает мир", False, why)
        check("после паузы мир идёт", False, why)

    # ---- resize
    page.set_viewport_size({"width": 900, "height": 600})
    page.wait_for_timeout(1500)
    sz = page.evaluate("() => { const c = document.querySelector('canvas'); return c ? [c.clientWidth, c.clientHeight,"
                       " innerWidth, innerHeight] : null; }")
    check("холст следует за окном", sz and abs(sz[0] - sz[2]) <= 2 and abs(sz[1] - sz[3]) <= 2, f"холст/окно {sz}")
    report["ошибок_всего_десктоп"] = len(errors)
    ctx.close()

    # ---- mobile, 3x screen
    e0 = len(errors)
    ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(("console", m.text)) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(("page", str(e))))
    page.goto("file:///" + os.path.abspath(PAGE).replace("\\", "/"), wait_until="load", timeout=120000)
    page.wait_for_timeout(6000)
    enter(page, {})
    shot(page, "моб-01-старт")
    m = page.evaluate("""() => { const c = document.querySelector('canvas');
        return {scrollW: document.documentElement.scrollWidth, w: innerWidth,
                ratio: c ? c.width / c.clientWidth : 0}; }""")
    report["мобильный"] = m
    check("мобильный: нет прокрутки вбок", m["scrollW"] <= m["w"] + 1, f"ширина страницы {m['scrollW']} при окне {m['w']}")
    check("pixel ratio ограничен (экран 3x)", 0 < m["ratio"] <= 2.01, f"холст рисует в {m['ratio']:.2f}x")
    toggles = [b for b in page.query_selector_all("button, [aria-expanded], summary")
               if b.is_visible() and re.search(r"☰|menu|controls|panel|toggle|hide|show|collapse|expand|⌄|▾|▸|−|\+",
                                               (label_of(page, b) + " " + (b.get_attribute("aria-expanded") or "")
                                                + " " + (b.get_attribute("class") or "")), re.I)]
    report["мобильный"]["переключатели_панелей"] = [label_of(page, t) for t in toggles][:6]
    folded = False
    covered_after = None
    if toggles:
        shown = """() => [...document.querySelectorAll('button, input')].map((e, i) => { const r = e.getBoundingClientRect();
            const inwin = r.width > 0 && r.height > 0 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;
            const vis = inwin && (e.checkVisibility ? e.checkVisibility({opacityProperty: true, visibilityProperty: true}) : true);
            if (!vis) return null;
            const t = document.elementFromPoint(Math.min(innerWidth - 1, Math.max(0, r.left + r.width / 2)),
                                                Math.min(innerHeight - 1, Math.max(0, r.top + r.height / 2)));
            return [i, !!t && (t === e || e.contains(t))]; }).filter(Boolean)"""
        s0 = page.evaluate(shown)
        try:
            toggles[0].click(timeout=5000)
        except Exception:
            pass
        # a panel slides in with a CSS transition, slow under software WebGL: wait until what is shown settles (6 s)
        s1, prev = s0, None
        for _ in range(12):
            page.wait_for_timeout(500)
            s1 = page.evaluate(shown)
            if s1 == prev and s1 != s0:
                break
            prev = s1
        folded = sorted(i for i, _ in s0) != sorted(i for i, _ in s1)
        covered_after = sum(1 for _, ok in s1 if not ok)
        report["мобильный"]["видно_до_после"] = [len(s0), len(s1)]
        report["мобильный"]["перекрыто_после"] = covered_after
        shot(page, "моб-02-панели-переключены")
    check("мобильный: панели сворачиваются", folded, "переключатель не найден или ничего не меняет")
    check("мобильный: раскрытые панели не перекрывают кнопки", covered_after == 0,
          "переключателя нет" if covered_after is None else f"после переключения перекрыто кнопок/ползунков: {covered_after}")
    report["ошибок_мобильный"] = len(errors) - e0
    if len(errors) > e0:
        report["косяки"].append("мобильный: ошибки " + "; ".join(x[1][:120] for x in errors[e0:e0 + 2]))
    ctx.close()
    br.close()

report["ошибки"] = [f"{k}: {t[:200]}" for k, t in errors][:40]
report["ошибок_всего"] = len(errors)
passed = sum(1 for v in report["проверки"].values() if v["ok"])
report["прошло"] = f"{passed}/{len(report['проверки'])}"
json.dump(report, open(os.path.join(DIR, "report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: report[k] for k in ("страница", "прошло", "ошибок_всего", "кнопок_видно")}, ensure_ascii=False))
for k in report["косяки"]:
    print("  -", k)
