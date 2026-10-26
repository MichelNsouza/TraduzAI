# adapters/ — Adaptadores específicos por jogo/engine

Adaptadores são **específicos** (Nível C) e não devem ir para `workspace/scripts/`. Eles encapsulam regras particulares de um jogo, engine ou formato: tabelas hardcoded, ranges, ponteiros, lógica de reinserção específica etc.

Regras:
- 1 diretório por jogo/engine: `adapters/<nome-jogo-plataforma>/`
- Sempre documentar: jogo, plataforma, status, referências (ROM hacking notes), limitações
- Não promover para `workspace/scripts/` a menos que seja completamente agnóstico e com docstring exigida
- Podem depender de scripts genéricos em `workspace/scripts/`
