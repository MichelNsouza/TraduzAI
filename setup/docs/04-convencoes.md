# Convenções de trabalho

## Regras gerais

- Nunca modificar arquivos originais.
- Trabalhar sempre em cópias.
- Relatórios por etapa em `workspace/reports/`.
- Registrar hipóteses e decisões nos relatórios.
- Resolver erros sozinho antes de pedir ajuda.

## Promoção de material ao repositório

Só vai ao repositório o que ajuda **outros jogos**.

- **Scripts**: mover para `workspace/scripts/` com docstring obrigatória:
  - propósito;
  - como usar (exemplo de comando);
  - dependências;
  - como generalizar (o que é específico do jogo).
- **Docs**: `workspace/context/`, 1 doc por descoberta/formato/lição.
- **Glossário**: `workspace/context/glossario.md` (termos EN→PT do jogo).
- **Templates**: `workspace/context/templates/`.

## Reutilização

- Procure em `workspace/scripts/` antes de recriar.
- Prefira adaptar um script existente a escrever do zero.
- Promova, nunca duplique.

## Formatos aceitos no material de apoio

- Markdown (docs), Python (scripts) e arquivos de apoio (templates, detaches pequenos, hexdumps).
- Arquivos grandes (ISO, bin, mídia) **nunca** vão ao repositório.