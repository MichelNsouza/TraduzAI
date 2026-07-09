#!/usr/bin/env bash
set -e

sudo dnf install -y \
python3 \
python3-pip \
git \
p7zip \
p7zip-plugins \
tree \
file \
ripgrep \
binwalk \
ffmpeg \
ImageMagick

echo "TraduzAI: ambiente Fedora instalado com sucesso."

echo
echo "OBS: Caso o ffmpeg não seja encontrado, habilite o RPM Fusion."
