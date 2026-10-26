# projects/ — Configurações por jogo

Cada jogo/tradução tem sua própria configuração aqui (versionado de forma leve).

Crie um diretório por projeto:
```text
workspace/projects/<nome-jogo>/
├── project.yaml
└── (opcionais: glossario.json, tabela.tbl)
```

Regras:
- `project.yaml` define plataforma, caminhos, ferramentas, adaptadores
- Não commitar ISOs ou ROMs
- Glossários e TBLs pequenos podem ser versionados aqui se genéricos o suficiente ou específicos do projeto
