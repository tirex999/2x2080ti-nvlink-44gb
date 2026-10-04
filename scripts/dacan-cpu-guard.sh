#!/bin/bash
# 28.09.2026: сторож ядер узла .105 (слово хозяина «откалибруй так, чтобы это все жило одновременно, приоритет на ст200»).
# DACAN (CT 200, пул на ЦП 0-63, главный цикл на ЦП 32) и ВМ 105 BaisonWin11 (50 vCPU) делят один узел.
# DACAN читает промпт или отвечает (/status busy или очередь) -> ВМ 105 прижата до GUARD_CPUS ядер; простой GUARD_HOLD с ->
# снова без предела. Период квоты короткий (10 мс): гостю Windows простой вида «всем vCPU стоять 90 мс из 100» вреден
# (CLOCK_WATCHDOG_TIMEOUT), с периодом 10 мс vCPU стоят не дольше нескольких мс.
# Остановка службы всегда снимает предел (ExecStopPost в dacan-cpu-guard.service).
# Калибровка 28.09 14:19-14:31 (/root/calib_guard2.sh: один и тот же жадный ответ 1929 токенов, по 3 раза на условие,
# decode_tok_s движка; Baison в ВМ 105 ел 47-49 ЦП): ВМ как есть 64.9 т/с; предел 16 ЦП - 67.6; 8 - 68.0; 4 - 68.3.
# Раскладка ВМ по ЦП (0-127 против 64-127 без 96) разницы не дала (64.9/65.2, 67.8/68.0). Колено - 16 ЦП: почти весь
# выигрыш (+4 %), а ВМ во время ответа сохраняет треть процессора.
URL=${GUARD_URL:-http://192.168.1.214:8000/status}
CG=${GUARD_CGROUP:-/sys/fs/cgroup/qemu.slice/105.scope/cpu.max}
Q=${GUARD_CPUS:-16}
HOLD=${GUARD_HOLD:-10}
PER=10000
last=0                                   # когда DACAN последний раз был занят
while true; do
  s=$(curl -s -m 2 "$URL")
  now=$(date +%s)
  if [[ $s =~ \"busy\":\ *true || $s =~ \"queued\":\ *[1-9] ]]; then last=$now; fi
  if (( now - last < HOLD )); then want="$((Q * PER)) $PER"; else want="max"; fi
  if [[ -f $CG ]]; then
    cur=$(<"$CG")
    if [[ $want == max ]]; then
      [[ $cur == max\ * ]] || { echo "max $PER" > "$CG" && echo "$(date +%T) ВМ 105 без предела (DACAN свободен)"; }
    elif [[ $cur != "$want" ]]; then
      echo "$want" > "$CG" && echo "$(date +%T) ВМ 105 прижата до $Q ЦП (DACAN занят)"
    fi
  fi
  sleep 0.5
done
