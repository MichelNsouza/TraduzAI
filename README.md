# TraduzAI

Projeto experimental para utilizar Inteligência Artificial na tradução de jogos antigos.

## Objetivo

Automatizar o máximo possível o processo de localização de jogos utilizando agentes de IA.

Fluxo esperado:

1. Analisar a ISO
2. Extrair arquivos
3. Identificar formatos conhecidos
4. Localizar textos
5. Exportar textos
6. Traduzir
7. Reinserir
8. Reconstruir a ISO
9. Validar no emulador

## Estrutura

workspace/input/     ISO original (nunca modificar)

workspace/extracted/ Conteúdo extraído (efêmero)

workspace/output/    Resultado final (efêmero)

workspace/reports/   Relatórios por etapa (efêmero)

workspace/context/   Conhecimento acumulado (versionado)

workspace/scripts/   Scripts reutilizáveis (versionado)

setup/               Instalação e docs do agente

## Instalação

- **Linux (nativo):** `setup/install.sh` ou scripts em `setup/install/`
- **Windows (WSL2 recomendado):** veja `setup/docs/06-windows.md`
- **Windows (nativo):** `setup/install/windows/install.ps1` e `check.ps1`

## Aviso Legal e Responsabilidade

- **Somente ROMs/ISOs legais:** Utilize apenas cópias de jogos que você possui fisicamente. Não distribuímos, hospedamos ou incentivamos a obtenção ilegal de ROMs, ISOs ou imagens de jogos.
- **Uso por conta e risco:** Este projeto é fornecido "no estado em que se encontra", sem garantias de qualquer tipo. O uso é de inteira responsabilidade do usuário.
- **Isenção de responsabilidade:** Os autores e colaboradores não se responsabilizam por qualquer uso indevido, danos, perdas ou consequências legais decorrentes do uso deste software.
- **Finalidade educacional/pesquisa:** Destinado a fins educacionais, pesquisa e preservação, respeitando as leis aplicáveis em seu país.

## Status

MVP em desenvolvimento.
