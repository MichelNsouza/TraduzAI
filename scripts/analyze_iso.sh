#!/usr/bin/env bash

set -e

ISO_DIR="workspace"
EXTRACT_DIR="extracted"
REPORT_DIR="reports"

ISO=$(find "$ISO_DIR" -maxdepth 1 -type f \( -iname "*.iso" -o -iname "*.bin" \) | head -n 1)

if [ -z "$ISO" ]; then
    echo "Nenhuma ISO encontrada em $ISO_DIR"
    echo "Coloque o arquivo do jogo em workspace/"
    exit 1
fi

echo "=================================="
echo " TraduzAI - ISO Analyzer"
echo "=================================="
echo ""

echo "ISO encontrada:"
echo "$ISO"
echo ""

mkdir -p "$EXTRACT_DIR"
mkdir -p "$REPORT_DIR"

GAME_NAME=$(basename "$ISO")
REPORT="$REPORT_DIR/${GAME_NAME}.md"

echo "Extraindo arquivos..."

rm -rf "$EXTRACT_DIR"/*
7z x "$ISO" -o"$EXTRACT_DIR" >/dev/null

echo "Gerando relatório..."

cat > "$REPORT" <<REPORT
# Relatório de Análise ISO

## Arquivo

$ISO

## Data

$(date)

## Estrutura encontrada

REPORT

echo '```' >> "$REPORT"
tree "$EXTRACT_DIR" >> "$REPORT"
echo '```' >> "$REPORT"

cat >> "$REPORT" <<REPORT

## Tipos de arquivos

REPORT

echo '```' >> "$REPORT"
find "$EXTRACT_DIR" -type f -exec file {} \; >> "$REPORT"
echo '```' >> "$REPORT"

cat >> "$REPORT" <<REPORT

## Strings encontradas

REPORT

echo '```' >> "$REPORT"
find "$EXTRACT_DIR" -type f -exec strings {} \; | head -n 200 >> "$REPORT"
echo '```' >> "$REPORT"

echo ""
echo "Análise concluída."
echo "Relatório criado:"
echo "$REPORT"
