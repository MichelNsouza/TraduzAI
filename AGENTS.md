# TraduzAI - Agent Instructions

## Objetivo

Automatizar a tradução de jogos antigos utilizando IA.

## Fluxo obrigatório

1. Analisar a ISO
2. Extrair arquivos
3. Identificar formatos conhecidos
4. Localizar textos
5. Exportar textos
6. Traduzir
7. Reinserir
8. Reconstruir a ISO
9. Validar no emulador

## Regras

- Nunca modificar a ISO original.
- Trabalhar sempre em cópias.
- Gerar relatórios em reports/.
- Criar scripts em scripts/.
- Preferir Python.
- Reutilizar scripts existentes.
- Tentar resolver erros automaticamente antes de pedir ajuda.

## Organização

workspace/
    ISO original

extracted/
    Conteúdo extraído

output/
    Resultado final

reports/
    Relatórios

scripts/
    Scripts auxiliares
