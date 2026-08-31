#!/usr/bin/env bash
# Установка готовой сборки vLLM для 2x RTX 2080 Ti — одной командой.
#
# Скрипт НИЧЕГО не собирает: скачивает уже скомпилированные колёса из релиза
# и ставит их с зависимостями. Компилятор, CUDA-тулкит и заголовки не нужны —
# они нужны только тому, кто собирает сам.
#
# Сначала проверяет машину и, если не подходит, говорит ПОЧЕМУ и что делать
# вместо — а не падает посреди процесса на пятом гигабайте.
#
#   bash install.sh                    поставить в ~/vllm-2080ti
#   bash install.sh --check            только проверить машину
#   bash install.sh --dir /opt/vllm    другой каталог
#   bash install.sh --model ORG/NAME   ещё и скачать модель с HuggingFace
#   bash install.sh --service          ещё и завести службу systemd
set -uo pipefail

REL_BASE="https://github.com/tirex999/2x2080ti-nvlink-44gb/releases/download/vllm-0.2.1rc3-sm75-cu130"
TARBALL="vllm-2080ti-sm75-cu130-wheels.tar.gz"
TORCH_INDEX="https://download.pytorch.org/whl/cu130"
NEED_GLIBC="2.38"

DIR="$HOME/vllm-2080ti"
CHECK_ONLY=0
MODEL=""
WITH_SERVICE=0
PORT=8000

while (($#)); do
  case "$1" in
    --check)   CHECK_ONLY=1; shift ;;
    --dir)     DIR="$2"; shift 2 ;;
    --model)   MODEL="$2"; shift 2 ;;
    --service) WITH_SERVICE=1; shift ;;
    --port)    PORT="$2"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "неизвестный ключ: $1"; exit 2 ;;
  esac
done

R=$'\033[31m'; G=$'\033[32m'; Y=$'\033[33m'; B=$'\033[1m'; O=$'\033[0m'
ok()  { printf "  ${G}v${O} %s\n" "$*"; }
no()  { printf "  ${R}x${O} %s\n" "$*"; }
hm()  { printf "  ${Y}!${O} %s\n" "$*"; }
die() { printf "\n${R}${B}Остановка.${O} %s\n\n" "$*"; exit 1; }
vge() { [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]; }

echo
echo "${B}Проверка машины${O}"
[ -r /etc/os-release ] && . /etc/os-release && ok "система: ${PRETTY_NAME:-неизвестна}"

GLIBC=$(ldd --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+$')
if [ -n "$GLIBC" ] && vge "$GLIBC" "$NEED_GLIBC"; then
  ok "glibc $GLIBC (нужно $NEED_GLIBC и новее)"
else
  no "glibc ${GLIBC:-неизвестна} — нужно $NEED_GLIBC и новее"
  BAD_GLIBC=1
fi

PY=""
for c in python3.12 python3; do
  command -v "$c" >/dev/null 2>&1 || continue
  V=$("$c" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null) || continue
  [ "$V" = "3.12" ] && { PY="$c"; break; }
done
if [ -n "$PY" ]; then
  ok "python 3.12: $PY"
else
  no "python 3.12 не найден (колёса под cp312, другой версией pip их не возьмёт)"
  BAD_PY=1
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
  if [ -n "$DRV" ]; then
    ok "драйвер $DRV"
    nvidia-smi --query-gpu=index,name,memory.total,compute_cap --format=csv,noheader 2>/dev/null |
      while IFS= read -r l; do printf "      %s\n" "$l"; done
    CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1)
    [ "$CC" = "7.5" ] || hm "архитектура $CC, а сборка под 7.5 (Turing)"
    vge "${DRV%%.*}" "580" || hm "драйвер $DRV может быть старым для CUDA 13"
  else
    no "nvidia-smi есть, но карт не видит"
    BAD_GPU=1
  fi
else
  no "nvidia-smi не найден"
  if [ -e /dev/nvidia0 ]; then
    hm "но /dev/nvidia0 есть — значит вы в контейнере с проброшенными картами."
    hm "Внутрь контейнера нужны userspace-библиотеки ТОЙ ЖЕ версии, что на хосте:"
    hm "  ./NVIDIA-Linux-x86_64-<версия>.run --no-kernel-module --silent"
    hm "Модуль ядра ставится только на хосте, в контейнере он не нужен."
  fi
  BAD_GPU=1
fi

FREE=$(df -Pk "$(dirname "$DIR")" 2>/dev/null | awk 'NR==2{print int($4/1048576)}')
if [ -n "$FREE" ]; then
  [ "$FREE" -ge 12 ] && ok "свободно ${FREE} ГБ" || hm "свободно ${FREE} ГБ, а нужно около 12"
fi

echo
if [ -n "${BAD_GLIBC:-}${BAD_PY:-}" ]; then
  echo "${B}Готовая сборка на этой машине не заработает.${O}"
  if [ -n "${BAD_PY:-}" ]; then
    echo "  Питон: колёса собраны под cp312. На Ubuntu 22.04 системный 3.10, и pip"
    echo "         отказывает сразу: 'is not a supported wheel on this platform'."
  fi
  if [ -n "${BAD_GLIBC:-}" ]; then
    echo "  glibc: в сборке есть символ __isoc23_strtol из glibc 2.38 — его подставляет"
    echo "         GCC 15, берущий C23-вариант strtol по умолчанию."
  fi
  echo
  echo "  ${B}Что делать:${O} собрать ветку 0.1.x самому. Она живёт на Ubuntu 22.04 с"
  echo "  GCC 11.4 и CUDA 12.8 и даёт 80.1 / 92.4 / 80.9 t/s против 87.0 / 99.6 / 88.0"
  echo "  у 0.2.x. Разница 8-12 процентов, а не разы. Подробности в docs/forks.md"
  echo
  exit 1
fi
[ -n "${BAD_GPU:-}" ] && hm "карты сейчас не видны — поставить можно, запустить нет"
echo "${B}Машина подходит.${O}"
[ "$CHECK_ONLY" = "1" ] && { echo; exit 0; }

echo
echo "${B}Установка в $DIR${O}"
mkdir -p "$DIR" || die "не могу создать $DIR"
cd "$DIR" || die "не могу зайти в $DIR"

if command -v apt-get >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
  echo "  ставлю системные пакеты..."
  DEBIAN_FRONTEND=noninteractive apt-get -qq update >/dev/null 2>&1
  DEBIAN_FRONTEND=noninteractive apt-get -qq install -y curl python3.12-venv >/dev/null 2>&1 \
    && ok "curl и python3.12-venv" || hm "apt не отработал, продолжаю"
fi

echo "  качаю готовую сборку..."
curl -fsSL -o "$TARBALL" "$REL_BASE/$TARBALL" || die "не скачался $REL_BASE/$TARBALL"
tar xzf "$TARBALL" || die "архив не распаковался"
if command -v md5sum >/dev/null 2>&1 && [ -f MD5SUMS.txt ]; then
  md5sum -c MD5SUMS.txt >/dev/null 2>&1 \
    && ok "контрольные суммы совпали" \
    || die "контрольные суммы НЕ совпали — скачайте заново"
fi

echo "  создаю окружение..."
"$PY" -m venv "$DIR/venv" || die "venv не создался (нужен пакет python3.12-venv)"
PIP="$DIR/venv/bin/pip"
"$PIP" -q install --upgrade pip >/dev/null 2>&1

echo "  ставлю torch cu130 (несколько гигабайт, это долго)..."
"$PIP" install -q torch==2.13.0 torchvision==0.28.0 torchaudio==2.11.0 \
  --index-url "$TORCH_INDEX" || die "torch не встал"
ok "torch поставлен"

echo "  ставлю остальные зависимости..."
"$PIP" install -q flashinfer-python==0.6.16.post3 "transformers>=5.5.3" numpy \
  || die "зависимости не встали"

echo "  ставлю сам движок..."
"$PIP" install -q ./vllm-*.whl || die "vllm не встал"
# flash_qla ставится БЕЗ разрешения зависимостей намеренно. В его метаданных
# прибиты tilelang==0.1.8 и apache-tvm-ffi==0.1.9, а vllm требует 0.1.12 и
# 0.1.11 — pip такое не решает и падает с ResolutionImpossible. На рабочем
# стенде стоят версии из vllm (0.1.12 / 0.1.11), и flash_qla с ними работает:
# его пины просто устарели. Проверено прямым замером на живом сервере.
"$PIP" install -q --no-deps ./flash_qla-*.whl || die "flash_qla не встал"
ok "движок поставлен"

echo
echo "${B}Проверка установленного${O}"
"$DIR/venv/bin/python" - <<'PY'
import importlib
import sys
try:
    import torch
    print("  v torch", torch.__version__, "| cuda", torch.version.cuda)
    n = torch.cuda.device_count()
    print("  %s карт видно: %d" % ("v" if n else "!", n))
    for i in range(n):
        p = torch.cuda.get_device_properties(i)
        print("      GPU%d %s, %.0f ГБ, sm_%d%d"
              % (i, p.name, p.total_memory / 1e9, p.major, p.minor))
except Exception as e:
    print("  x torch:", e)
    sys.exit(1)
try:
    import vllm
    print("  v vllm", vllm.__version__)
    importlib.import_module("vllm._C_stable_libtorch")
    print("  v скомпилированные ядра загрузились")
    import flash_qla
    print("  v flash_qla")
except Exception as e:
    print("  x", type(e).__name__, str(e)[:300])
    sys.exit(1)
PY
[ $? -eq 0 ] || die "поставилось, но проверка не прошла — смотрите ошибку выше"

if [ -n "$MODEL" ]; then
  echo
  echo "${B}Качаю модель $MODEL${O}"
  "$PIP" -q install huggingface_hub >/dev/null 2>&1
  HF_HUB_DISABLE_XET=1 "$DIR/venv/bin/python" - "$MODEL" "$DIR/models" <<'PY'
import os
import sys
from huggingface_hub import snapshot_download
repo, base = sys.argv[1], sys.argv[2]
dest = os.path.join(base, repo.split("/")[-1])
print("  ->", dest)
snapshot_download(repo_id=repo, local_dir=dest, max_workers=8)
print("  готово")
PY
fi

if [ "$WITH_SERVICE" = "1" ] && [ "$(id -u)" = "0" ]; then
  echo
  echo "${B}Завожу службу${O}"
  MD=""
  [ -n "$MODEL" ] && MD="$DIR/models/${MODEL##*/}"
  cat > /etc/systemd/system/vllm-2080ti.service <<UNIT
[Unit]
Description=vLLM 0.2.1-pre3 на 2x RTX 2080 Ti
After=network-online.target
StartLimitIntervalSec=3600
StartLimitBurst=6

[Service]
Type=simple
Environment=HOME=/root
WorkingDirectory=$DIR
ExecStart=$DIR/venv/bin/python -m vllm.entrypoints.openai.api_server \\
  --model ${MD:-ВПИШИТЕ_ПУТЬ_К_МОДЕЛИ} \\
  --host 0.0.0.0 --port $PORT \\
  --tensor-parallel-size 2 --dtype half \\
  --gpu-memory-utilization 0.94 \\
  --max-model-len 102400 \\
  --max-num-seqs 1 \\
  --speculative-config '{"method":"mtp","num_speculative_tokens":4}' \\
  --enable-auto-tool-choice --tool-call-parser qwen3_xml \\
  --enable-force-include-usage
Restart=on-failure
RestartSec=30
TimeoutStartSec=1800
KillMode=mixed

[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  ok "юнит: /etc/systemd/system/vllm-2080ti.service"
  [ -z "$MD" ] && hm "путь к модели не задан — впишите его в юнит перед запуском"
fi

echo
echo "${B}Готово.${O} Запуск вручную:"
echo
echo "  source $DIR/venv/bin/activate"
echo "  python -m vllm.entrypoints.openai.api_server --model <путь> \\"
echo "      --tensor-parallel-size 2 --dtype half --gpu-memory-utilization 0.94 \\"
echo "      --max-model-len 102400 --max-num-seqs 1 \\"
echo "      --speculative-config '{\"method\":\"mtp\",\"num_speculative_tokens\":4}'"
echo
echo "  MAX_NUM_SEQS=1 не ради экономии: батч больше единицы вместе с MTP и"
echo "  CUDA-графом роняет сервер на Turing. Разбор в docs/pitfalls.md"
echo
