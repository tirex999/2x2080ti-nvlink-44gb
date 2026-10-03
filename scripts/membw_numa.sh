#!/bin/bash
# Полоса памяти двухсокетной машины с закреплением по NUMA и без (замер 03.10.2026, docs/results.md, раздел 4).
# Инструмент — membw.c рядом (STREAM triad, OpenMP, first-touch, лучшее из трёх):
#   gcc -O3 -march=native -fopenmp -o membw membw.c
# Запуск: ./membw_numa.sh [путь к membw] [ГиБ на массив]   -> таблица в membw_numa.log
# Нужен numactl. На узлах должно быть свободно не меньше 3×ГиБ: привязка к узлу без свободной памяти
# (--membind) кончается OOM, и под раздачу может попасть не этот тест, а соседний процесс.
# STATUS_URL (необязательно) — /status движка на том же узле, чтобы видеть, не мешал ли он прогону.
set -u
MB=${1:-./membw}
GIB=${2:-4}
LOG=membw_numa.log
: > "$LOG"
st() {
  [ -n "${STATUS_URL:-}" ] || { echo "-"; return; }
  curl -s -m 2 "$STATUS_URL" | python3 -c 'import json,sys; d=json.load(sys.stdin); print("занят" if d.get("busy") or d.get("queued") else "свободен")' 2>/dev/null || echo "?"
}
run() {  # run <подпись> <потоков> <закреп 0|1> [аргументы numactl...]
  local lab=$1 t=$2 pin=$3; shift 3
  local s1 r pre=""
  s1=$(st)
  [ $# -gt 0 ] && pre="numactl $*"
  if [ "$pin" = 1 ]; then r=$(OMP_PROC_BIND=spread OMP_PLACES=cores $pre "$MB" "$GIB" "$t" 2>&1)
  else r=$(env -u OMP_PROC_BIND -u OMP_PLACES $pre "$MB" "$GIB" "$t" 2>&1); fi
  printf "%-44s %4s  %-7s %7s  (движок %s/%s)\n" "$lab" "$t" "$([ "$pin" = 1 ] && echo закреп || echo нет)" \
    "$(echo "$r" | grep -oE 'TRIAD [0-9.]+' | awk '{print $2}')" "$s1" "$(st)" >> "$LOG"
  sleep 3
}
{
  echo "== полоса памяти $(hostname) $(date '+%d.%m.%Y %H:%M'), массивы $GIB ГиБ x3"
  numactl -H | grep -E "^node [0-9]+ (size|free)"
  echo "загрузка: $(cat /proc/loadavg)"
  printf "%-44s %4s  %-7s %7s\n" "конфигурация" "пот." "потоки" "TRIAD"
} >> "$LOG"
for k in 1 2; do
  echo "-- вся машина, first-touch, круг $k" >> "$LOG"
  for t in 16 32 64 96 128; do run "вся машина" $t 0; run "вся машина" $t 1; done
done
echo "-- чередование страниц по узлам" >> "$LOG"
for t in 32 64 128; do run "вся машина, --interleave=all" $t 0 --interleave=all; done
run "вся машина, --interleave=all" 64 1 --interleave=all
echo "-- один сокет" >> "$LOG"
run "сокет 0, своя память (узел 0)" 32 1 --cpunodebind=0 --membind=0
run "сокет 0, своя память (узел 0)" 32 0 --cpunodebind=0 --membind=0
run "сокет 1, своя память (узел 1)" 32 1 --cpunodebind=1 --membind=1
run "сокет 1, своя память (узел 1)" 32 0 --cpunodebind=1 --membind=1
run "сокет 0, чужая память (узел 1, UPI)" 32 1 --cpunodebind=0 --membind=1
run "сокет 1, чужая память (узел 0, UPI)" 32 1 --cpunodebind=1 --membind=0
echo "-- оба сокета, вся память на одном узле" >> "$LOG"
for m in 0 1; do
  run "оба сокета, вся память на узле $m" 64 1 --membind=$m
  run "оба сокета, вся память на узле $m" 64 0 --membind=$m
done
echo "== ГОТОВО $(date '+%H:%M:%S')" >> "$LOG"
