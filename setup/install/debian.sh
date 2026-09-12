#!/usr/bin/env bash
set -e

sudo apt update

sudo apt install -y \
python3 \
python3-pip \
git \
p7zip-full \
tree \
file \
ripgrep \
binwalk \
ffmpeg \
imagemagick

echo "TraduzAI: ambiente Debian instalado com sucesso."
