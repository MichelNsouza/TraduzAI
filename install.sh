#!/usr/bin/env bash

set -e

echo "=================================="
echo " TraduzAI - Environment Check"
echo "=================================="

check() {
    if command -v "$1" >/dev/null 2>&1; then
        printf "✔ %-15s encontrado\n" "$1"
    else
        printf "✘ %-15s não encontrado\n" "$1"
    fi
}

echo
echo "Ferramentas instaladas:"
echo

check python
check pip
check 7z
check tree
check file
check rg
check binwalk
check ffmpeg
check convert

echo
echo "Verificação concluída."
