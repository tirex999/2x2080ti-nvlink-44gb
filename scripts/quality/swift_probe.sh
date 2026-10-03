#!/bin/bash
# Swift 1.5 шаг 1 (03.10.2026, слово Вадима «Делай все по очереди»): Swift GSQ-RCO IQ3_XXS против базового
# ISTA GSQ-RCO IQ3_XXS на одном движке DACAN, одинаковые задачи (хомяки, аквариум; low / medium / xhigh), выборка
# галереи (bench_ext.py: T 0.6, top_p 0.95, top_k 20). Служба strata-serve на время снята; trap возвращает её всегда.
# Журнал /root/swift_probe_0310.log, галерея /root/gallery_0310.
set -u
LOG=/root/swift_probe_0310.log
Q=/root/quality_0310
exec >> "$LOG" 2>&1
say() { echo "$(date '+%H:%M:%S') $*"; }

stop_engines() {
    systemctl stop strata-serve strata-swift-test strata-ista-test 2>/dev/null
    for i in $(seq 1 90); do pgrep -f "[s]trata_srv_h4" >/dev/null || break; sleep 2; done
    pgrep -f "[s]trata_srv_h4" >/dev/null && { say "движок не вышел за 180 с"; return 1; }
    return 0
}
restore() {
    say "возврат штатной службы"
    stop_engines
    systemctl start strata-serve
    for i in $(seq 1 120); do curl -s -m 2 http://127.0.0.1:8000/status | grep -q busy && break; sleep 10; done
    say "штатная служба: $(systemctl is-active strata-serve), /status: $(curl -s -m 2 http://127.0.0.1:8000/status | cut -c1-60)"
    say "== ГОТОВО"
}
trap restore EXIT

up() {  # up <имя>: поднять движок с /root/strata19/strata-serve.<имя>.json и дождаться /status
    local n=$1
    stop_engines || return 1
    : > /root/strata19/strata-serve-$n.log
    systemd-run --unit=strata-$n-test --collect -p WorkingDirectory=/root/strata19 /bin/bash -c \
      "/bin/bash /root/strata19/zhdat_karty.sh; exec /root/strata/.venv/bin/python -u /root/strata19/serve/server.py --engine strata --config /root/strata19/strata-serve.$n.json --port 8000 --host 0.0.0.0" >/dev/null
    say "движок $n запущен, жду /status"
    for i in $(seq 1 180); do
        curl -s -m 2 http://127.0.0.1:8000/status | grep -q busy && { say "движок $n готов"; grep -E "expert cache|VRAM free with everything" /root/strata19/strata-serve-$n.log | tail -3; return 0; }
        systemctl is-active -q strata-$n-test || { say "движок $n упал"; tail -20 /root/strata19/strata-serve-$n.log; return 1; }
        sleep 10
    done
    say "движок $n не поднялся за 30 мин"; return 1
}

bench() {  # bench <подпись> <полное имя> <квант>
    for key in хомяки аквариум; do
        for lvl in low medium xhigh; do
            say "задача $key $lvl"
            (cd $Q && BENCH_BASE=http://127.0.0.1:8000 BENCH_CTX=262144 BENCH_OUT=/root/gallery_0310 \
                python3 bench_ext.py "$key" 1 "$1" "$2" "$3" "$lvl" 2>&1 | grep -vE "^задача:|^проверок:")
        done
    done
}

say "== начало"
up swift && bench "Swift 1.5 IQ3_XXS Дацан 2x2080Ti 256K" \
    "ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF IQ3_XXS" "3 бита (GSQ-RCO)"
grep -E "strata serve: prompt" /root/strata19/strata-serve-swift.log | tail -6
up ista && bench "Flash-Next ISTA IQ3_XXS Дацан 2x2080Ti 256K" \
    "ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF IQ3_XXS (таблица n-грамм Q8_0)" "3 бита (GSQ-RCO)"
grep -E "strata serve: prompt" /root/strata19/strata-serve-ista.log | tail -6
