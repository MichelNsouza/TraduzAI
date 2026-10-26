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

## Status

MVP em desenvolvimento.
