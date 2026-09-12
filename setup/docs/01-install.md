# Instalação do ambiente

O TraduzAI utiliza ferramentas de engenharia reversa, scripts Python e agentes de Inteligência Artificial.

## Sistemas suportados

- Arch Linux / CachyOS
- Ubuntu
- Debian
- Fedora
- openSUSE

## Instalação

Entre na pasta install e execute o instalador correspondente ao seu sistema.

Exemplo:

./arch.sh

Após instalar, valide o ambiente:

./check.sh

## Observações

- Ambientes Debian/Ubuntu precisam de `python3-venv` (já coberto pelos instaladores).
- ImageMagick: use `convert` (IM6) ou `magick` (IM7) — os instaladores cobrem ambos.
- Ferramentas opcionais: QuickBMS (extração avançada) e um emulador PS1 (validação) — instale conforme necessário.
