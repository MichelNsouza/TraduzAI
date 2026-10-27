# Formatos de texto — Final Fantasy I & II: Dawn of Souls (GBA)

Descobertas de engenharia reversa aplicáveis a outros jogos de GBA com texto
em Shift-JIS ou páginas de glifos de 16 bits.

ROM: `Final Fantasy I & II - Dawn of Souls (GBA, US)`, 16 MiB
(`0x01000000`), header `FF1&2DAWNOFS`, game code `BFFE`.

## 1. Texto do FF1 — Shift-JIS com ASCII intercalado

- Cada caractere imprimível é um par **big-endian** Shift-JIS
  (`0x81-0x84` + `0x40-0xFC`), decodificável com `cp932`.
- O texto da tradução oficial usa as formas **fullwidth** (`Ａ-Ｚ`, `ａ-ｚ`,
  `０-９`, `，．？！’”－／＊：`) e o espaço ideográfico `U+3000`.
- `0x00` termina a string.
- `0x0A` = quebra de linha. Outros bytes `< 0x20` são códigos de controle do
  motor (`0x01, 0x05, 0x08, 0x09, 0x0C, 0x0F, 0x10`).
- `0x87 XX` = ícone (word `0x87XX`), usado antes de nomes de itens/magias.
- **ASCII de 1 byte aparece intercalado** para especificadores de formato:
  `%0`, `%1`, `%2`, `%2d`, `%s`, `%d`. É o mesmo esquema do `printf`: o motor
  substitui por nome/quantidade em tempo de execução. **Nunca converta esses
  trechos para fullwidth** — o especificador deixaria de funcionar.

Decodificador mínimo:

```python
for b in data[off:]:
    if b == 0: break
    if b < 0x20: controle(b)          # 0x0A = \n
    elif b < 0x80: ascii(chr(b))      # %0, %2d, %s
    else: cp932(par_de_2_bytes)       # 2 bytes
```

## 2. Texto do FF2 — página de glifos de 16 bits

O script principal do FF2 não usa Shift-JIS: usa códigos de 16 bits
**little-endian** numa página própria.

| código | caractere | código | caractere |
|--------|-----------|--------|-----------|
| `0x00-0x09` | `0-9` | `0x0A-0x23` | `A-Z` |
| `0x24-0x3D` | `a-z` | `0x40` | `,` |
| `0x41` | `.` | `0x43` | `;` |
| `0x44` | `?` | `0x45` | `!` |
| `0x4C` | `'` | `0x4E` | `"` |
| `0xFB` | `-` | `0xFF` | `-` (travessão) |
| `0xF8` | `/` (nomes internos) | `0x0100` | `~` |
| `0x80F9` | espaço | `0x80F0` | quebra de linha |
| `0x80FF` | terminador | | |

Relação com ASCII: `A-Z` = `código + 0x37`, `a-z` = `código + 0x3D`.
Digitos ficam em `0x00-0x09` (não em `0x30`). Códigos fora da tabela
(`0x0100`, `0xFA`, `0xF9`, `0x47`) são marcadores do motor e devem ser
preservados como tokens.

## 3. Tabelas de ponteiros

- Ponteiros são words de 32 bits (`0x08xxxxxx` = `0x08000000 + offset`).
- Strings ficam alinhadas em 4 bytes e separadas por `0x00`.
- As tabelas são **arrays contíguos** de ponteiros; detectam-se varrendo o ROM
  por sequências de ≥15 words válidas cujos destinos decodificam como texto.

Tabelas do FF1 (offset, entradas):

```
0x00040304   25  nomes de locais
0x0019E650  651  itens (nomes + descrições)
0x001A1650  204  magias
0x001A3E84  221  termos de menu
0x001A4344   20  magia negra
0x001A4470   20  magia branca
0x001A4D0C   15  itens-chave
0x001A5030   56  interface
0x001BE32C   34  nomes de mapa
0x001DC9F8   15  elementos
0x001DDD38  195  bestiário A
0x00210370 2560  diálogo do FF1 (1273 strings únicas)
0x00215CAC  195  bestiário B
0x002267A4  195  bestiário C
0x0022D0D8  195  bestiário D
0x002331A0  169  nomes de monstros
0x00EDF15C   29  configuração
0x00EDF1FC   27  rótulos de menu
0x00EDF6C0   61  final/epílogo
```

FF2: `0x002601C0`, 4256 ponteiros; strings contíguas em
`0x00264440-0x00295E7E`.

**Atenção — o FF2 não guarda mensagens completas em ordem de história.** A
tabela aponta para um **pool de linhas/fragmentos individuais, ordenado por
sufixo e deduplicado**. Várias mensagens compartilham a mesma linha, e uma fala
do jogo é a concatenação de entradas consecutivas do pool. Consequências:

- Traduzir entrada a entrada preserva a contagem e a ordem das entradas (seguro
  para o motor), mas a concordância entre linhas vizinhas pode ficar imperfeita.
- Não tente "remontar" as mensagens: a mesma entrada é reutilizada em contextos
  diferentes e não há um limite explícito de mensagem.
- Rótulos de mapa e mensagens de evento podem ocupar 1 ou 2 linhas; nesse caso
  a entrada já contém `0x80F0` e deve ser traduzida como bloco de 2 linhas.
- Algumas entradas são apenas fragmentos (`imperador!{C:FA}`, `{C:F9}What is
  this place?`); tokens `{C:XX}` precisam ser preservados.

Tabelas detectadas mas **não traduzíveis** (dados/opções internas):
`0x1DA25C` (dados de fonte), `0x216F70`, `0x2369EC`, `0x238814`,
`0x2388D8`, `0x25A954`, `0x2965DC` (só códigos de controle) e `0xEDF7B8`
(menu de debug em japonês).

## 4. Reinserção segura

Estratégia usada (funciona sem emulador e sem realocar blocos inteiros):

1. Extrair todas as strings referenciadas por tabela.
2. Reencodar as traduções e gravá-las **no espaço livre** no fim do ROM
   (`0x00EE0760-0x01000000`, ~1,17 MiB de `0xFF`).
3. Atualizar cada entrada de ponteiro para o novo endereço.
4. **Não apagar o texto original.** Se alguma referência não mapeada existir
   (ponteiro em código, tabela secundária), ela continua apontando para texto
   válido — no pior caso a linha permanece em inglês, nunca corrompida.

Espaço: ~253 mil caracteres no total. FF1 = 2 bytes/caractere, FF2 = 2
bytes/caractere; a estimativa conservadora de planejamento era ~700 KB, dentro
do espaço livre (a execução real gravou menos, graças à deduplicação — ver
números abaixo).

Números da execução final (referência):

- 8.216 traduções carregadas, **6.220 strings únicas** (deduplicadas).
- 392.137 bytes de texto único, último byte em `0xF420A7`.
- 778.072 bytes de espaço livre restantes (de 1.177.760).
- Diff: 412.646 bytes alterados; **nenhum** fora dos 8.216 `ptr_site` e do
  espaço livre; a região livre era 100% `0xFF` antes.
- `verify`: 8.216 ok, 0 divergentes.

## 5. Fonte e acentos

O ROM não possui glifos acentuados para o latim (confirmado no visualizador de
fonte interno: `FONT 8x8`, `FONT 12x12`, com listagem de caracteres sem
acentos). Consequências:

- A tradução deve ser **transliterada para ASCII** na hora da reinserção
  (`á→a`, `ã→a`, `ç→c`, `é→e`, ...), mantendo os acentos nos CSVs.
- Caracteres sem glifo são normalizados (ex.: `(`/`)` removidos, `%` →
  " por cento", `;` → `,`). Ver `_FF1_REPS`/`_FF2_REPS` no adaptador.
- Adicionar acentos exigiria editar os bitmaps da fonte e remapear códigos
  SJIS não usados — trabalho futuro, não necessário para jogar.

## 6. Armadilhas encontradas

- A heurística "UTF-16 little-endian" usada em tentativas anteriores estava
  errada para o FF1: gerava offsets deslocados e textos vazios.
- Varrer o ROM inteiro por pares SJIS válidos encontra **falsos positivos**
  em gráficos/dados (blocos de kanji/kana e desenhos de caixa). A validação
  boa é exigir que o início da string esteja referenciado por uma tabela de
  ponteiros.
- Ponteiros de 4 bytes lidos em offsets desalinhados geram milhares de
  falsos ponteiros; sempre varrer offsets múltiplos de 4.
- O decodificador precisa aceitar ASCII de 1 byte, senão ~25 strings com
  `%0/%2d/%s` falham e ficam sem tradução.

## 7. Armadilhas de verificação e layout

- O `insert` faz `strip("\n")` antes de codificar: um newline inicial usado só
  para posicionar a mensagem é removido. A re-extração, portanto, não bate
  literalmente com o CSV nesse ponto; o `verify` normaliza e confirma o
  conteúdo.
- O `verify` compara a tradução **sanitizada** (ASCII, sem acentos) com o texto
  re-extraído, normalizando espaços, `NFKC` e aspas tipográficas. Diferenças de
  padding/centralização não são detectadas por ele — para checar centralização,
  compare a posição do texto dentro da linha original.
- O `verify` não detecta overflow: uma string pode estar correta e ainda assim
  ser mais larga que a caixa/menu original. Meça o comprimento por linha se
  isso importar.
- **Não** aplique o requebra automático (`relayout_csv.py`) ao `ff1.csv`: ele
  reescreve parágrafos e destrói a estrutura de linhas/linhas em branco do FF1.
  Para o FF2, mensagens centralizadas de uma linha devem ser recentralizadas
  preservando o **centro original**, não a margem esquerda.

## 8. Diagnóstico: trava antes do título / ROM truncada

Sintoma reproduzido: a ROM completa boota, mas se o arquivo for **truncado no
ponto em que terminavam os dados originais** (`0xEE0760`), o jogo **trava antes
da tela de título** no gpSP. Motivo: as tabelas de ponteiros continuam no
arquivo, mas os ponteiros reescritos apontam para `0x08EE0760+`, além do fim do
arquivo truncado. O mGBA preenche a leitura fora do arquivo com `0xFF` e segue;
o gpSP não, e trava.

Consequências para suporte e para builds futuras:

- Sempre confirmar **tamanho exato** da ROM no aparelho: 16.777.216 bytes.
  Tamanhos menores (ex.: 15.599.456 = `0xEE0760`) indicam cópia truncada.
- Conferir o MD5 no destino; uma cópia por rede/cartão pode truncar.
- Se o aparelho/core não enxergar o fim da ROM, uma build **em lugar**
  (sem alterar ponteiros e sem usar o espaço livre) serve de diagnóstico:
  se ela boota e a completa não, o problema está no fim do arquivo/mapeamento,
  não na tradução em si.
- Não concluir que a ROM está corrompida só porque um core trava: testar o
  mesmo arquivo em mGBA e gpSP e comparar o tamanho/hash no destino separa
  corrupção de arquivo de diferença de core.
- Um arquivo truncado em `0xEE0760` ainda contém **todo o texto original**;
  a tradução é que fica inacessível. Por isso o sintoma é "antes do título"
  quando o boot lê ponteiros de configuração/menu, e não uma tela em inglês.
