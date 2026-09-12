# TraduzAI

Projeto experimental para utilizar Inteligência Artificial na tradução de jogos antigos.

## Objetivo

Automatizar o máximo possível o processo de localização de jogos utilizando agentes de IA.

Fluxo esperado:

1. Analisar uma ISO
2. Extrair seus arquivos
3. Identificar formatos
4. Localizar textos
5. Traduzir
6. Reinserir os textos
7. Reconstruir a ISO
8. Validar no emulador

## Estrutura

workspace/input/     ISO original (nunca modificar)

workspace/extracted/ Conteúdo extraído (efêmero)

workspace/output/    Resultado final (efêmero)

workspace/reports/   Relatórios por etapa (efêmero)

workspace/context/   Conhecimento acumulado (versionado)

workspace/scripts/   Scripts reutilizáveis (versionado)

setup/               Instalação e docs do agente

## Status

MVP em desenvolvimento.
