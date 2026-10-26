# FF1 GBA (Final Fantasy I & II: Dawn of Souls) - Adaptador

- **Jogo:** Final Fantasy I & II: Dawn of Souls
- **Plataforma:** Game Boy Advance
- **Tipo:** Adaptador específico (Nível C)
- **Status:** Experimental / POC
- **Base:** Tabela/notes baseadas em mapeamento Jeff Ludwig
- **Uso:** Extração experimental de strings para CSV no formato do TraduzAI

## Scripts
- `ff1dos_extract.py` - Extração por ranges conhecidos (class/names/items/weapons/armor/magic/monsters)
- `ff1dos_extract_clean.py` - Variante com limpeza
- `ff1dos_decode.py` - Decodificação com tabela hardcoded

## Notas
- Caminhos hardcoded em versões originais; ajustar para uso com projeto/config
- Não genérico - contém tabelas, ícones e ranges específicos
- Manter aqui, não promover para `workspace/scripts/`
