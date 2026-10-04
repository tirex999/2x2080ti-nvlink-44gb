#!/bin/bash
# Swift 1.5, третий квант (04.10.2026): NVFP4 по рецепту RadixArk (ModelOpt: эксперты NVFP4, остальное BF16, таблица FP8)
# на FreeToken — так же, как гоняли RadixArk/Qwen3.8-Flash-Next-NVFP4 (ft_nvfp4_numa.sh: одна карта, эксперты на AVX-512,
# банки по узлам NUMA). Ждёт конца конвертации и сверки (swift_modelopt_0410.log), снимает DACAN, поднимает FreeToken,
# гоняет задачи галереи, возвращает DACAN всегда. Журнал $LOG, задачи — TASKS, ожидание загрузки — UP_TRIES x 10 с.
set -u
LOG=${LOG:-/root/swift_probe_ft2_0410.log}
Q=/root/quality_0310
M=/LLM/models/ukisai/Swift1.5-Qwen3.8-Flash-Next-NVFP4
exec >> "$LOG" 2>&1
say() { echo "$(date '+%H:%M:%S') $*"; }

for i in $(seq 1 1080); do grep -q "== ГОТОВО" /root/swift_modelopt_0410.log && break; sleep 10; done
grep -q "== verify rc=0" /root/swift_modelopt_0410.log || { say "сверка чекпойнта не прошла или не дошла — FreeToken не запускаю"; tail -20 /root/swift_modelopt_0410.log; exit 1; }
say "чекпойнт сверен: $(grep -E 'имена/типы/формы' /root/swift_modelopt_0410.log)"

stop_all() {
    systemctl stop strata-serve ftserve-swift 2>/dev/null
    for i in $(seq 1 90); do pgrep -f "[s]trata_srv_h4|[f]t serve" >/dev/null || break; sleep 2; done
    pgrep -f "[s]trata_srv_h4|[f]t serve" >/dev/null && { say "движок не вышел за 180 с"; return 1; }
    return 0
}
restore() {
    say "возврат штатной службы"
    stop_all
    systemctl start strata-serve
    for i in $(seq 1 240); do curl -s -m 2 http://127.0.0.1:8000/status | grep -q busy && break; sleep 10; done
    say "штатная служба: $(systemctl is-active strata-serve), /status: $(curl -s -m 2 http://127.0.0.1:8000/status | cut -c1-60)"
    say "== ГОТОВО"
}
trap restore EXIT

sed "s#--model /LLM/models/flash-next-nvfp4#--model $M#" /root/ft_nvfp4_numa.sh > /root/ft_swift_numa.sh
grep -q -- "--model $M" /root/ft_swift_numa.sh || { say "в ft_swift_numa.sh не подставилась модель"; exit 1; }
stop_all || exit 1
free -g | head -2
systemd-run --unit=ftserve-swift --collect /bin/bash -c "exec /bin/bash /root/ft_swift_numa.sh >> /root/ft_swift.log 2>&1" >/dev/null
say "FreeToken запущен на $M, жду /health = ok (/v1/models он отдаёт ещё до загрузки весов — 04.10 так сорвался первый заход)"
for i in $(seq 1 ${UP_TRIES:-540}); do
    curl -s -m 3 http://127.0.0.1:1919/health | grep -q '"ok"' && { say "FreeToken готов: $(curl -s -m 3 http://127.0.0.1:1919/health | cut -c1-120)"; break; }
    systemctl is-active -q ftserve-swift || { say "FreeToken упал"; tail -30 /root/ft_swift.log; exit 1; }
    sleep 10
done
curl -s -m 3 http://127.0.0.1:1919/health | grep -q '"ok"' || { say "FreeToken не поднялся за $((${UP_TRIES:-540} / 6)) мин"; tail -30 /root/ft_swift.log; exit 1; }
free -g | head -2

for key in ${TASKS:-хомяки аквариум майнкрафт}; do
    for lvl in low medium xhigh; do
        say "задача $key $lvl"
        (cd $Q && BENCH_BASE=http://127.0.0.1:1919 BENCH_CTX=262144 BENCH_OUT=/root/gallery_0310 \
            python3 bench_ext.py "$key" 1 "Swift 1.5 NVFP4 RadixArk FreeToken NUMA 1x2080Ti" \
            "Swift 1.5 Flash-Next, свой квант из BF16 по рецепту RadixArk/ModelOpt: эксперты NVFP4, остальное BF16, таблица n-грамм FP8" \
            "4 бита (NVFP4)" "$lvl" 2>&1 | grep -vE "^задача:|^проверок:")
    done
done
grep -E "tok/s|throughput" /root/ft_swift.log | tail -5
