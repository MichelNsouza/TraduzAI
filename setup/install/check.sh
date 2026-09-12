#!/usr/bin/env bash

echo "=================================="
echo " TraduzAI Environment Check"
echo "=================================="
echo ""

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        printf "✓ %-15s OK\n" "$1"
    else
        printf "✗ %-15s AUSENTE\n" "$1"
    fi
}

echo "Sistema:"
if [ -f /etc/os-release ]; then
    grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"'
else
    echo "Sistema desconhecido"
fi

echo ""

echo "Ferramentas:"
check_command python
check_command python3
check_command pip
check_command git
check_command 7z
check_command tree
check_command file
check_command rg
check_command binwalk
check_command ffmpeg
check_command convert

echo ""

echo "Versões:"

if command -v python3 >/dev/null 2>&1; then
    python3 --version
fi

if command -v git >/dev/null 2>&1; then
    git --version
fi

echo ""

echo "Verificação concluída."
