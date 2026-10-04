# -*- coding: utf-8 -*-
# 28.09.2026: сравнение по КАЧЕСТВУ (слово хозяина «Скорости на флеше и так понятны, важно что он сделает по результату
# мозгов»): все прогоны галереи /LLM/hamsters по задачам и уровням размышления - проверок пройдено / всего, годен ли.
# Проверка «цикл анимации» пересчитывается и с setAnimationLoop (ложный провал: renderer.setAnimationLoop - тот же цикл).
import glob, json, os, re, sys, collections

GAL = os.environ.get("GALLERY", "gallery")   # у нас /LLM/hamsters
rows = collections.defaultdict(dict)       # (задача, модель) -> режим -> (проверок, всего, годен, токенов, т/с, пересчёт)
for jf in glob.glob(os.path.join(GAL, "*", "*.json")):
    try:
        d = json.load(open(jf, encoding="utf-8"))
    except Exception:
        continue
    if "задача" not in d or "проверок" not in d:
        continue
    task, group = d["задача"], d.get("модель", os.path.basename(os.path.dirname(jf)))
    model = group.split(" · ", 1)[1] if " · " in group else group
    mode = d.get("режим") or "?"
    hits, total = d.get("проверок", 0), d.get("всего_проверок", 0)
    fixed = hits
    if "цикл анимации" in (d.get("не_прошло") or []):
        html = jf[:-5] + ".html"
        try:
            if re.search(r"setAnimationLoop", open(html, encoding="utf-8", errors="replace").read()):
                fixed = hits + 1
        except OSError:
            pass
    good = bool(d.get("годен"))
    good_fixed = good or (d.get("финиш") == "stop" and fixed >= d.get("порог", 10**9) and fixed > hits)
    cur = rows[(task, model)].get(mode)
    rec = (hits, total, good, d.get("токенов"), d.get("токенов_в_секунду"), fixed, good_fixed)
    if cur is None or rec[5] > cur[5]:            # лучший прогон этого режима
        rows[(task, model)][mode] = rec

MODES = ["low", "medium", "xhigh"]
focus = sys.argv[1] if len(sys.argv) > 1 else "Flash-Next"
for task in sorted({t for t, _ in rows}):
    print(f"\n=== {task}")
    items = [(m, rows[(task, m)]) for (t, m) in rows if t == task and focus.lower() in m.lower()]
    def score(it):
        v = [x[5] / x[1] for x in it[1].values() if x[1]]
        return -(sum(v) / len(v)) if v else 0
    for m, md in sorted(items, key=score):
        cells = []
        for mo in MODES:
            if mo in md:
                h, tot, g, tok, ts, fx, gf = md[mo]
                cells.append(f"{fx}/{tot}{'' if fx == h else '*'}{'' if gf else ' нет'}")
            else:
                cells.append("—")
        print(f"  {m[:60]:60s} " + " | ".join(f"{c:12s}" for c in cells))
print("\n* - пересчитано: цикл анимации через setAnimationLoop засчитан")
