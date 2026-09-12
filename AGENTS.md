# TraduzAI - Agent Instructions

## Objetivo

Automatizar a tradução de jogos antigos utilizando IA, acumulando conhecimento e ferramentas reutilizáveis entre jogos.

## Trilha de leitura (ordem)

1. `README.md` — visão geral do projeto.
2. `setup/docs/01-install.md` — ambiente do sistema.
3. `setup/docs/02-agent.md` — configuração do agente.
4. `setup/docs/03-pipeline.md` — o ciclo de 9 etapas e os artefatos.
5. `setup/docs/04-convencoes.md` — regras de trabalho e de promoção de material.
6. `workspace/context/README.md` — conhecimento acumulado.
7. `workspace/scripts/README.md` — biblioteca de scripts reutilizáveis.

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
- Gerar relatórios por etapa em `workspace/reports/` (efêmeros).
- Destilar conhecimento reutilizável em `workspace/context/` (versionado).
- Promover scripts genéricos para `workspace/scripts/` (versionados).
- Reutilizar scripts existentes antes de recriar.
- Preferir Python.
- Tentar resolver erros automaticamente antes de pedir ajuda.

## Material de apoio (o que vai ao repositório)

- `workspace/context/` — docs, descobertas de engenharia reversa, formatos, glossários, lições de outros jogos e templates de relatório.
- `workspace/scripts/` — scripts agnósticos de jogo, com docstring (propósito, uso, dependências, generalização).
- Ao concluir uma etapa/jogo: promover o reutilizável; nunca duplicar.
- Relatórios e artefatos de trabalho **não** vão ao repositório.

## Organização

```
workspace/input/     ISO original (nunca tocar)
workspace/extracted/ Conteúdo extraído (efêmero)
workspace/output/    Resultado final (efêmero)
workspace/reports/   Relatórios por etapa (efêmero)
workspace/context/   Conhecimento acumulado (versionado)
workspace/scripts/   Scripts reutilizáveis (versionado)
setup/               Instalação e docs do agente
```