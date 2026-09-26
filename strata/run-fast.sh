#!/bin/bash
# Strata на двух картах как сервер с OpenAI API. Патч strata-2x2080ti.patch должен быть применён и собран.
#
#   STRATA=/путь/к/Strata PACK=<пакет модели> S1=<шард 1 .gguf> S2=<шард 2 .gguf> MTP=<каталог mtp/rt> bash run-fast.sh
#
# Главная карта MAIN (по умолчанию 1) с сокетом NODE (1), вторая карта SECOND (0) — как на нашем стенде.
set -e
STRATA=${STRATA:?путь к собранной Strata}; PACK=${PACK:?пакет модели}; S1=${S1:?шард 1}; S2=${S2:?шард 2}; MTP=${MTP:?mtp/rt}
HERE=$(cd "$(dirname "$0")" && pwd)
PROFILE=${PROFILE:-$HERE/data/profile_other_2609.bin}
USAGE=${USAGE:-$HERE/data/usage_other_2609.bin}
MAIN=${MAIN:-1}; SECOND=${SECOND:-0}; NODE=${NODE:-1}; CTX=${CTX:-131072}; PORT=${PORT:-8080}
PY=${PY:-$STRATA/.venv/bin/python}; CUDA_LIB=${CUDA_LIB:-/usr/local/cuda/lib64}

echo "прогрев кэша ОС таблицей n-грамм: $S2"
cat "$S2" > /dev/null

cat > "$STRATA/run-fast-exe.sh" <<EOW
#!/bin/sh
export CUDA_VISIBLE_DEVICES=$MAIN,$SECOND
exec numactl --cpunodebind=$NODE --membind=$NODE $STRATA/build/strata "\$@"
EOW
chmod +x "$STRATA/run-fast-exe.sh"

"$PY" - "$STRATA" "$PACK" "$S1" "$S2" "$MTP" "$CTX" "$PROFILE" "$USAGE" "$PORT" "$CUDA_LIB" <<'PYEOF'
import json, sys
strata, pack, s1, s2, rt, ctx, prof, usage, port, cuda_lib = sys.argv[1:]
args = ["--pack", pack, "--native", s1, "--ple-gguf", s2, "--ple-io", "mmap",
        "--expert-profile", prof, "--expert-cache", "auto", "--adapt-every", "0",
        "--second-card", "1", "--second-card-usage", usage, "--pcie-frac", "0",
        "--prefill", "2048", "--spec", "4", "--spec-min-p", "0.5", "--mtp", rt,
        "--max-context", ctx, "--kv", "int8"]
cfg = {"exe": strata + "/run-fast-exe.sh", "args": args, "cwd": strata, "tokenizer": pack + "/tokenizer",
       "model_name": "qwen3.8-flash-next-2x2080ti", "log": strata + "/strata-fast.log",
       "lib_dirs": [cuda_lib], "port": int(port)}
open(strata + "/strata-fast.json", "w").write(json.dumps(cfg, indent=1))
print(" ".join(args))
PYEOF

exec "$PY" -u "$STRATA/serve/server.py" --engine strata --config "$STRATA/strata-fast.json" --port "$PORT" --host 0.0.0.0
