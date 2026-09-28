# -*- coding: utf-8 -*-
# 28.09.2026: перепроверка галереи /LLM/hamsters по исправленной проверке «цикл анимации».
# Была regex requestAnimationFrame - ложный провал, когда цикл идёт через renderer.setAnimationLoop (тот же цикл three.js).
# Правило годности то же, что в bench_ext.py: финиш stop, в коде есть </html>, проверок не меньше порога.
# Сухой прогон по умолчанию; с аргументом --write правит JSON (копия всех JSON до правки - в /root/hamsters_json_bak_2809.tgz).
import glob, json, os, re, sys

GAL = os.environ.get("GALLERY", "gallery")   # у нас /LLM/hamsters
NEW = r"requestAnimationFrame|setAnimationLoop"
write = "--write" in sys.argv
fixed = flipped = 0
for jf in sorted(glob.glob(os.path.join(GAL, "*", "*.json"))):
    try:
        d = json.load(open(jf, encoding="utf-8"))
    except Exception:
        continue
    if "цикл анимации" not in (d.get("не_прошло") or []):
        continue
    try:
        code = open(jf[:-5] + ".html", encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    if not re.search(NEW, code, re.I):
        continue
    was = bool(d.get("годен"))
    d["не_прошло"] = [x for x in d["не_прошло"] if x != "цикл анимации"]
    d["прошло"] = list(d.get("прошло") or []) + ["цикл анимации"]
    d["проверок"] = d.get("проверок", 0) + 1
    d["годен"] = d.get("финиш") == "stop" and "</html>" in code.lower() and d["проверок"] >= d.get("порог", 10**9)
    d["перепроверено"] = "28.09.2026: цикл анимации через setAnimationLoop засчитан"
    fixed += 1
    flipped += (d["годен"] and not was)
    print(f"{'годен' if d['годен'] else 'нет  '}{' (было нет)' if d['годен'] and not was else '':12s} "
          f"{d['проверок']}/{d.get('всего_проверок')}  {os.path.relpath(jf, GAL)}")
    if write:
        json.dump(d, open(jf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nпересчитано прогонов: {fixed}, из них стали годными: {flipped}{'' if write else '  (сухой прогон)'}")
