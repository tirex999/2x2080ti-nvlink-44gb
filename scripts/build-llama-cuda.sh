#!/bin/bash
# Сборка llama.cpp под Turing (RTX 2080 Ti, sm_75).
#
# ГРАБЛЯ: nvcc может отсутствовать в PATH у systemd-службы, хотя в
# интерактивной оболочке он есть. Симптом — cmake падает на
# CMakeDetermineCUDACompiler с "No such file or directory". Поэтому ищем
# компилятор явно и передаём -DCMAKE_CUDA_COMPILER.
set -e

SRC=${1:?укажи каталог с исходниками llama.cpp}
JOBS=${2:-$(nproc)}

NVCC=$(ls -d /usr/local/cuda*/bin/nvcc 2>/dev/null | sort -V | tail -1)
[ -z "$NVCC" ] && NVCC=$(command -v nvcc || true)
if [ -z "$NVCC" ]; then
    echo "nvcc не найден — CUDA не установлена или не в /usr/local" >&2
    exit 1
fi
export CUDA_HOME=$(dirname "$(dirname "$NVCC")")
export PATH="$CUDA_HOME/bin:$PATH"
echo "nvcc: $NVCC"
"$NVCC" --version | tail -2

cmake -S "$SRC" -B "$SRC/build" \
      -DGGML_CUDA=ON \
      -DCMAKE_CUDA_ARCHITECTURES=75 \
      -DCMAKE_CUDA_COMPILER="$NVCC" \
      -DLLAMA_CURL=OFF \
      -DCMAKE_BUILD_TYPE=Release

cmake --build "$SRC/build" -j "$JOBS" --target llama-server llama-bench

ls -la "$SRC/build/bin/llama-server" "$SRC/build/bin/llama-bench"
