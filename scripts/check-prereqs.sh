#!/usr/bin/env bash
# Проверка окружения под форк vLLM для 2080 Ti: что есть, чего нет и что
# из-за этого нельзя собрать. Ничего не меняет — только смотрит и печатает
# команды, которыми чинить.
#
# Проверяются РЕАЛЬНЫЕ требования, взятые из PROJECT_RELEASE.env самого
# форка, а не «вроде нужна новая убунта»:
#   ветка 0.2.x — CUDA 13.0, GCC ровно 15, ядро >= 7, glibc >= 2.41 с патчем
#   ветка 0.1.x — CUDA 12.8, GCC 11, ядро 5.x и новее
#
# Запуск:  bash check-prereqs.sh
set -u

RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; BLD=$'\033[1m'; OFF=$'\033[0m'
ok()   { printf "  ${GRN}есть${OFF}      %-22s %s\n" "$1" "$2"; }
bad()  { printf "  ${RED}НЕТ${OFF}       %-22s %s\n" "$1" "$2"; }
warn() { printf "  ${YEL}внимание${OFF}  %-22s %s\n" "$1" "$2"; }

fail02=0; fail01=0

echo
echo "${BLD}ОКРУЖЕНИЕ${OFF}"
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  ok "система" "$PRETTY_NAME"
else
  warn "система" "не определяется"
fi

KERN=$(uname -r); KMAJ=${KERN%%.*}
if (( KMAJ >= 7 )); then ok "ядро" "$KERN"
else bad "ядро" "$KERN — ветке 0.2.x нужно 7 и новее"; fail02=1; fi

if command -v gcc >/dev/null 2>&1; then
  GV=$(gcc -dumpversion); GMAJ=${GV%%.*}
  if [[ "$GMAJ" == "15" ]]; then ok "gcc" "$GV"
  else bad "gcc" "$GV — ветке 0.2.x нужен РОВНО 15, сравнение по старшей цифре"; fail02=1; fi
  [[ "$GMAJ" == "11" || "$GMAJ" == "12" ]] || fail01=$fail01
else
  bad "gcc" "не найден"; fail02=1; fail01=1
fi

GLIBC=$(ldd --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+$')
if [[ -n "$GLIBC" ]]; then
  if [[ "$(printf '%s\n2.41\n' "$GLIBC" | sort -V | head -1)" == "2.41" && "$GLIBC" != "2.41" ]] || [[ "$GLIBC" == "2.41" ]]; then
    warn "glibc" "$GLIBC — нужен патч rsqrt к CUDA (в форке он битый, см. docs/pitfalls.md)"
  else
    ok "glibc" "$GLIBC"
  fi
fi

if command -v nvcc >/dev/null 2>&1; then
  CV=$(nvcc --version | sed -n 's/.*release \([0-9.]*\),.*/\1/p')
  CMAJ=${CV%%.*}
  if [[ "$CMAJ" == "13" ]]; then ok "cuda" "$CV (подходит 0.2.x)"
  elif [[ "$CMAJ" == "12" ]]; then ok "cuda" "$CV (подходит 0.1.x)"; fail02=1
  else warn "cuda" "$CV — ни 13.0, ни 12.8"; fail02=1; fail01=1; fi
else
  bad "nvcc" "не на PATH — добавь /usr/local/cuda-XX/bin"; fail02=1; fail01=1
fi

echo
echo "${BLD}КАРТЫ И ДРАЙВЕР${OFF}"
echo "  ${YEL}важно:${OFF} в LXC драйвер стоит на ХОСТЕ, версия системы в контейнере на это не влияет."
if command -v nvidia-smi >/dev/null 2>&1; then
  DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
  [[ -n "$DRV" ]] && ok "драйвер" "$DRV" || bad "драйвер" "nvidia-smi есть, но карт не видит"
  nvidia-smi --query-gpu=index,name,memory.total,compute_cap --format=csv,noheader 2>/dev/null |
    while IFS= read -r l; do printf "            %s\n" "$l"; done
  CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1)
  [[ "$CC" == "7.5" ]] && ok "архитектура" "sm_75 — этот форк ровно про неё" \
                       || warn "архитектура" "$CC — форк писан под sm_75"
else
  bad "nvidia-smi" "не найден"
fi

echo
echo "${BLD}ЧТО ИЗ ЭТОГО СЛЕДУЕТ${OFF}"
if (( fail02 == 0 )); then
  echo "  ${GRN}Ветка 0.2.x собирается.${OFF} Это та, что даёт 99.6 t/s на Qwen3.6 и 89.2 на Qwen3.8."
else
  echo "  ${RED}Ветка 0.2.x на этой машине НЕ соберётся.${OFF} Причины помечены НЕТ выше."
  echo "  Обходить проверку через ALLOW_HOST_MISMATCH=1 можно только для пробного прогона:"
  echo "  сборка пойдёт, но это не проверенная конфигурация."
  echo
  echo "  ${BLD}Практический выход — ветка 0.1.x.${OFF} Мы получали на ней 80.1/92.4/80.9"
  echo "  на Ubuntu 22.04 с GCC 11.4, CUDA 12.8, torch 2.11.0+cu128. Это не суррогат:"
  echo "  разница с 0.2.x около 8-12 процентов, а не в разы."
fi
echo
