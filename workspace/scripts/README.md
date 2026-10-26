# scripts/ — Biblioteca reutilizável

Scripts **agnósticos de jogo**, versionados. 

**Apenas scripts genéricos vão aqui.** Adaptadores específicos por jogo/engine vão em `adapters/`.

## Convenção de docstring (obrigatória)
Todo script promovido deve ter docstring com:
- **propósito**: para que serve
- **como usar**: exemplo de comando
- **dependências**: ferramentas/bibliotecas necessárias
- **como generalizar**: o que é específico do jogo (deve ser "nenhum" ou claramente evitado)

## Regras
- Reutilize antes de recriar
- Promova, não duplique
- Se tiver tabelas/ranges/nomes de arquivo hardcoded específicos de jogo → mover para `adapters/`
