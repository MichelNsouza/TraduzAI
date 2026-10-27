# Contribuindo com o TraduzAI

O TraduzAI cresce com o conhecimento gerado a cada tradução. A ideia é simples: **scripts genéricos, descobertas e contextos reutilizáveis devem voltar para o repositório**.

## Como contribuir

1. Fork do repositório
2. Crie uma branch: `git checkout -b feature/sua-contribuicao`
3. Faça suas alterações seguindo as regras abaixo
4. Abra um Pull Request com descrição clara

## O que contribuir

| Tipo | Onde | Requisitos |
|---|---|---|
| **Scripts agnósticos** | `workspace/scripts/` | Devem ter docstring obrigatória (propósito, como usar, dependências, como generalizar). Não podem ter paths/nomes/ranges hardcoded de um jogo específico. |
| **Descobertas de engenharia reversa** | `workspace/context/` | Documente formatos, tabelas de caracteres, ponteiros, compressão, engines etc. Um arquivo `.md` por descoberta. |
| **Lições aprendidas** | `workspace/context/` | O que funcionou, o que deu errado e como resolver. Ajuda muito futuros agentes/jogadores. |
| **Glossários reutilizáveis** | `workspace/context/` | Termos, siglas, nomes próprios. Prefira formatados e claros. |
| **Adaptadores** | `adapters/` | Se for muito específico de um jogo/engine, coloque em `adapters/<jogo-plataforma>/` com README explicando. |
| **Melhorias na infraestrutura** | `core/` | Melhorias em orquestração, registry, schemas, validação etc. São sempre bem-vindas. |
| **Documentação** | `setup/docs/` ou raiz | Correções, traduções ou explicações que ajudem iniciantes. |

## O que **não** contribuir

- **ROMs, ISOs, BINs, imagens** - Nunca. Use apenas cópias legais do seu próprio jogo.
- **Arquivos grandes** (> alguns MB) - Evite subir dumps, logs gigantes ou backups desnecessários.
- **Dados pessoais** - Chaves, tokens, emails, caminhos com informações sensíveis.
- **Scripts específicos** - Se tiver tabelas, offsets, nomes de arquivos hardcoded específicos do jogo, coloque em `adapters/` ao invés de `workspace/scripts/`.

## Regras de promoção

Conforme definido em `AGENTS.md`:
- **Promova** o que for reutilizável por outros jogos
- **Não duplique** - procure em `workspace/scripts/` e `workspace/context/` antes de criar
- **Relatórios e artefatos efêmeros** (`workspace/reports/`, `workspace/extracted/`, `workspace/output/`) não vão para o repo
- **CSV de tradução** - Não suba CSVs completos de jogos, a menos que sejam exemplos mínimos e anonimizados

## Dica para agentes
Se você está usando um agente de IA durante a sessão de tradução, peça para ele **destilar** ao final: identificar scripts/contextos/glossários reutilizáveis e movê-los para os locais corretus com documentação adequada.

## Código de conduta
Seja respeitoso, colaborativo e mantenha o foco em **ferramentas, scripts, descobertas e contexto** ao invés de ROMs.

## Licença
Ao contribuir, você concorda que suas contribuições serão disponibilizadas sob a mesma licença do projeto.
