# FF1 GBA (Final Fantasy I & II: Dawn of Souls) — Adaptador

- **Jogo:** Final Fantasy I & II: Dawn of Souls
- **Plataforma:** Game Boy Advance (ROM US, game code `BFFE`)
- **Tipo:** Adaptador específico (Nível C)
- **Status:** funcional — extração, tradução e reinserção completas

## Scripts

| Script | Função |
|--------|--------|
| `ff12dos_text.py` | codec (FF1 Shift-JIS / FF2 glifos 16-bit), descoberta das tabelas, extração, reinserção e verificação. Único arquivo necessário. |
| `glossario.json` | pós-edição de nomes/termos para o tradutor automático. |

Os arquivos `ff1dos_extract.py`, `ff1dos_extract_clean.py` e `ff1dos_decode.py`
são da primeira tentativa (encoding errado: assumiam UTF-16 little-endian e
offsets fixos). Foram mantidos apenas como histórico; **não usar**.

## Uso

```bash
# 1) extrair textos -> CSV + manifest
python3 adapters/ff1_gba_dos/ff12dos_text.py extract \
    --rom workspace/extracted/ff1ff2dos_gba/rom_original.gba \
    --out-dir workspace/output/ff1ff2dos_gba/text

# 2) traduzir (offline, Argos en->pt + pós-edição PT-BR)
python3 workspace/scripts/translate_csv_argos.py \
    --csv workspace/output/ff1ff2dos_gba/text/ff1.csv \
          workspace/output/ff1ff2dos_gba/text/ff2.csv \
    --out-dir workspace/output/ff1ff2dos_gba/traducao \
    --glossary adapters/ff1_gba_dos/glossario.json

# 3) reinserir
python3 adapters/ff1_gba_dos/ff12dos_text.py insert \
    --rom workspace/extracted/ff1ff2dos_gba/rom_original.gba \
    --manifest workspace/output/ff1ff2dos_gba/text/manifest.json \
    --csv workspace/output/ff1ff2dos_gba/traducao/ff1.csv \
          workspace/output/ff1ff2dos_gba/traducao/ff2.csv \
          workspace/output/ff1ff2dos_gba/traducao/manual.csv \
    --out workspace/output/ff1ff2dos_gba/FF1-2-Dawn-of-Souls-PTBR.gba

# 4) verificar (re-extrai o ROM gerado e compara com as traduções)
python3 adapters/ff1_gba_dos/ff12dos_text.py verify \
    --rom workspace/output/ff1ff2dos_gba/FF1-2-Dawn-of-Souls-PTBR.gba \
    --manifest workspace/output/ff1ff2dos_gba/text/manifest.json \
    --csv workspace/output/ff1ff2dos_gba/traducao/ff1.csv \
          workspace/output/ff1ff2dos_gba/traducao/ff2.csv \
          workspace/output/ff1ff2dos_gba/traducao/manual.csv
```

## O que é traduzido

- FF1: 4.886 entradas válidas em 19 tabelas (4.887 slots; 1 inválido) —
  diálogo, itens, magias, menus, bestiário, mapas, final. Tabelas de opções
  internas e o menu de debug em japonês são ignorados de propósito.
- FF2: 4.256 entradas do script principal (história, batalhas, menus).
- Não há textos de imagem (gráficos com letras) — só texto de tabela.

## FF2: pool de linhas, não mensagens

A tabela `0x2601C0` aponta para um **pool de linhas/fragmentos individuais,
ordenado por sufixo e deduplicado** (`0x264440-0x295E7E`). Uma fala do jogo é a
concatenação de entradas consecutivas. Por isso cada entrada é traduzida no
lugar: a contagem e a ordem são preservadas, mas a concordância entre linhas
vizinhas pode ficar imperfeita. Rótulos de mapa/eventos de 2 linhas já contêm
`0x80F0` e devem ser traduzidos como bloco.

## Limitações conhecidas

- **Sem acentos:** a fonte do ROM não tem glifos acentuados; a inserção
  translitera (`ção→cao`). Os CSVs mantêm os acentos para edição futura.
- **Overflow:** o português é mais longo que o inglês. Aproximadamente 1.442
  linhas do FF1 e 1.872 do FF2 têm alguma linha mais larga que a original;
  descrições de itens/magias e alguns nomes de menu podem ser cortados.
- Tradução automática (Argos) com pós-edição PT-BR: boa para jogar, mas não
  substitui revisão humana.
- Sem emulador disponível no ambiente: a validação é estrutural (re-extração
  + comparação byte a byte), não visual.
- Strings de tabelas não mapeadas por ponteiro permanecem em inglês (não há
  nenhuma conhecida com texto real).

## Estado final da execução

- 8.216 traduções inseridas, 6.220 strings únicas (deduplicadas).
- 392.137 bytes de texto, último byte em `0xF420A7`; 778.072 bytes livres.
- `verify`: 8.216 ok, 0 divergentes (1 aviso pré-existente em `ff1_config`).
- Diff limpo: alterações apenas nos 8.216 `ptr_site` e no espaço livre (que era
  100% `0xFF`). Header `FF1&2DAWNOFS`/`BFFE` preservado.
- ROM: `workspace/output/ff1ff2dos_gba/FF1-2-Dawn-of-Souls-PTBR.gba`
  (MD5 `45d206cb88a4404b6e0f8a4388395c6a`).

## Notas de engenharia reversa

Ver `workspace/context/gba-ff1-ff2-dos-text-formats.md` (encodings, tabelas,
estratégia de reinserção, armadilhas).
