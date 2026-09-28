#!/bin/bash
# 28.09.2026: калибровка сторожа ядер .105, второй проход с исправленной методикой. Первый (окна по 40 с по одному
# длинному ответу) утонул в дрейфе содержимого: одно и то же условие «как есть» дало 50.6 и 58.9 т/с - MTP принимает код
# и размышление по-разному. Здесь в каждом условии один и тот же жадный ответ (temperature 0 -> одинаковый текст,
# одинаковый приём MTP), 3 раза, скорость - decode_tok_s самого движка (/metrics requests), без max_tokens.
# Журнал /root/calib_guard2.log, итог строкой «^== ЧЧ:ММ:СС ГОТОВО$».
URL=http://192.168.1.214:8000
CG=/sys/fs/cgroup/qemu.slice/105.scope
P=$(cat /var/run/qemu-server/105.pid)
ALL=0-127; OFF=64-95,97-127
REP=${REP:-3}
use() { awk '/usage_usec/{print $2}' $CG/cpu.stat; }
setaff() { taskset -a -p -c "$1" $P > /dev/null; }
setq() { if [ "$1" = max ]; then echo "max 10000" > $CG/cpu.max; else echo "$(( $1 * 10000 )) 10000" > $CG/cpu.max; fi; }
cleanup() { setaff $ALL; echo "max 100000" > $CG/cpu.max; }
trap cleanup EXIT
body='{"model":"x","stream":false,"temperature":0,"reasoning_effort":"low","messages":[{"role":"user","content":"Напиши на Python класс LRU-кэша с ограничением по памяти в байтах: get, put, удаление старых записей, статистика попаданий. Дай код и коротко объясни решения."}]}'
last() { curl -s -m 5 $URL/metrics | python3 -c '
import json,sys; r=json.load(sys.stdin)["requests"][0]   # /metrics: newest first
print(r.get("output_tokens"), r.get("decode_tok_s"), r.get("prompt_ms"), r.get("finish"))'; }
echo "$(date +%T) старт; прогрев одним ответом"
curl -s -m 900 $URL/v1/chat/completions -H 'Content-Type: application/json' -d "$body" > /dev/null; echo "  прогрев: $(last)"
cond() {   # cond <имя> <affinity> <предел>
  setaff "$2"; setq "$3"; sleep 2
  local u0=$(use) t0=$(date +%s.%N) rates=""
  for i in $(seq 1 $REP); do
    curl -s -m 900 $URL/v1/chat/completions -H 'Content-Type: application/json' -d "$body" > /dev/null
    read -r n ts pm fin <<< "$(last)"; rates="$rates $ts"; toks="$toks $n"
  done
  local u1=$(use) t1=$(date +%s.%N)
  awk -v n="$1" -v r="$rates" -v k="$toks" -v u=$((u1-u0)) -v t0=$t0 -v t1=$t1 'BEGIN{
    m=split(r,a," "); s=0; for(i=1;i<=m;i++) s+=a[i];
    printf "%-26s DACAN %5.1f т/с (%s )  токенов%s   ВМ 105 %5.1f ЦП\n", n, s/m, r, k, u/1e6/(t1-t0)}'
  toks=""
}
cond "как есть (0-127)"      $ALL max
cond "64-127 без 96"         $OFF max
cond "64-127, предел 16"     $OFF 16
cond "64-127, предел 8"      $OFF 8
cond "64-127, предел 4"      $OFF 4
cond "0-127, предел 8"       $ALL 8
cond "0-127, предел 4"       $ALL 4
cond "как есть снова"        $ALL max
echo "== $(date +%T) ГОТОВО"
