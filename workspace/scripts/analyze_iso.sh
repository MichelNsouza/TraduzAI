#!/usr/bin/env bash

set -e

ISO_DIR="workspace/input"
EXTRACT_DIR="workspace/extracted"
REPORT_DIR="workspace/reports"

ISO=$(find "$ISO_DIR" -maxdepth 1 -type f \( -iname "*.iso" -o -iname "*.bin" \) | head -n 1)

if [ -z "$ISO" ]; then
    echo "Nenhuma ISO encontrada em $ISO_DIR"
    echo "Coloque o arquivo do jogo em workspace/input/"
    exit 1
fi

echo "=================================="
echo " TraduzAI - ISO Analyzer"
echo "=================================="
echo ""

echo "ISO encontrada:"
echo "$ISO"
echo ""

echo "Calculando SHA256..."
sha256sum "$ISO" >> "$REPORT" 2>/dev/null || shasum -a 256 "$ISO" >> "$REPORT" 2>/dev/null || true
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

## SHA256

REPORT

sha256sum "$ISO" 2>/dev/null | awk '{print $1}' >> "$REPORT" || shasum -a 256 "$ISO" 2>/dev/null | awk '{print $1}' >> "$REPORT" || echo "N/A" >> "$REPORT"

cat >> "$REPORT" <<REPORT

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
