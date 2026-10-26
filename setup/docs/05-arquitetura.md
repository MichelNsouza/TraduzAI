# Arquitetura do TraduzAI

## Visão geral
TraduzAI é uma plataforma modular para tradução de jogos retrô assistida por IA. 
Separação clara entre genérico (reutilizável) e específico (adaptadores por jogo/engine).

## Estrutura
- `core/` - Orquestrador, schemas, registry, adapters base, pipeline
- `adapters/` - Adaptadores específicos por jogo/engine (Nível C)
- `workspace/scripts/` - Scripts agnósticos apenas (Nível A/B)
- `workspace/context/` - Conhecimento acumulado versionado
- `workspace/projects/` - Configurações por projeto/jogo
- `tools/` - Wrappers próprios quando necessário

## Níveis
- **Nível A**: Infraestrutura genérica (hash, cópias, relatórios, logs)
- **Nível B**: Reutilizáveis por formato/plataforma (TBL, descompressão, scanner)
- **Nível C**: Adaptadores específicos (regras por jogo/engine)

## Tool Registry
`core/registry/tools.yaml` cataloga ferramentas com automação, licença, plataformas, limitações.
Agentes consultam registry para escolher ferramentas corretas.

## Fluxo
1. Analisar ISO (com hash)
2. Extrair arquivos
3. Identificar formatos
4. Localizar textos
5. Exportar textos (CSV schema: id,original,traducao,status,nota)
6. Traduzir (LLM + glossário/TM)
7. Reinserir (preservando estrutura)
8. Reconstruir ISO
9. Validar no emulador
