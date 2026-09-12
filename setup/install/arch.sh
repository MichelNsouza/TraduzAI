#!/usr/bin/env bash
set -e

sudo pacman -Syu --needed \
python \
python-pip \
git \
p7zip \
tree \
file \
ripgrep \
binwalk \
ffmpeg \
imagemagick

echo "TraduzAI: ambiente Arch instalado com sucesso."
