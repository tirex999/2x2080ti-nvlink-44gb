#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка тождества скорости для спекулятивного декодирования.

    скорость генерации = средняя длина принятого × (темп черновика / MTP_K)

Смысл второй скобки: темп черновой головы, делённый на число черновых
токенов, это число ПРОХОДОВ модели в секунду — константа железа. Всё
остальное лишь то, сколько токенов удаётся снять с одного прохода.

Печатается МАКСИМАЛЬНАЯ невязка, а не средняя: средняя спрячет отдельные
промахи, а вопрос ровно в том, точная связь или приблизительная.

    python3 verify_mtp_identity.py docs/data/mtp-throughput-2026-08-31.tsv [MTP_K]
"""
import io
import sys


def load(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        head = None
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if head is None:
                head = parts
                continue
            r = dict(zip(head, parts))
            try:
                gen = float(r["gen_tps"])
                acc = float(r["acc_len"])
                dr = float(r["drafted_tps"])
            except (ValueError, KeyError):
                continue          # окно без спекулятивной статистики
            rows.append((r["utc"], gen, acc, dr))
    return rows


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "docs/data/mtp-throughput-2026-08-31.tsv"
    k = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0
    rows = load(path)

    # Обрывки отбрасываю по ЯВНОМУ признаку: генерация или черновик почти
    # не работали в этом окне. Это не подгонка — это окна, где усреднение
    # за 10 секунд просто не имеет смысла, и они помечены самими числами.
    work = [r for r in rows if r[1] > 1.0 and r[3] > 1.0]
    frag = len(rows) - len(work)

    print("файл: %s   MTP_K=%g" % (path, k))
    print("окон со статистикой: %d, из них рабочих: %d, обрывков: %d"
          % (len(rows), len(work), frag))
    if not work:
        return

    ok = 0
    worst = (0.0, None)
    steps = []
    for utc, gen, acc, dr in work:
        st = dr / k
        steps.append(st)
        pred = acc * st
        err = abs(pred - gen) / gen * 100.0
        if err <= 1.0:
            ok += 1
        if err > worst[0]:
            worst = (err, (utc, gen, pred, acc, st))

    steps.sort()
    print()
    print("  сходится в пределах 1 %%: %d из %d (%.1f %%)"
          % (ok, len(work), 100.0 * ok / len(work)))
    print("  максимальная невязка:    %.2f %%" % worst[0])
    if worst[1]:
        utc, gen, pred, acc, st = worst[1]
        print("    худшее окно %s: журнал %.1f, формула %.1f (длина %.2f, шагов %.2f/с)"
              % (utc, gen, pred, acc, st))
    print()
    print("  ПРОХОДОВ В СЕКУНДУ (константа железа):")
    print("    мин %.2f   медиана %.2f   макс %.2f"
          % (steps[0], steps[len(steps) // 2], steps[-1]))
    print()
    print("  примеры:")
    for utc, gen, acc, dr in work[-5:]:
        print("    %s   %.2f × %.2f = %6.2f   в журнале %6.1f"
              % (utc, acc, dr / k, acc * dr / k, gen))


if __name__ == "__main__":
    main()
