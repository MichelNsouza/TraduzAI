#!/usr/bin/env python3
"""Codec, extractor and inserter for Final Fantasy I & II: Dawn of Souls (GBA, US).

Jogo: Final Fantasy I & II - Dawn of Souls (GBA, BFFE)
Status: funcional (extracao/reinsercao por tabela de ponteiros)

Formatos de texto
-----------------
FF1 (FINAL FANTASY I):
  - Shift-JIS big-endian. Cada caractere imprimivel ocupa 2 bytes
    (0x81-0x84 + 0x40-0xFC); o texto usa as formas "fullwidth" (Ａ-Ｚ, ａ-ｚ,
    ０-９, ，．？！’”－／＊：) e espaco ideografico U+3000.
  - 0x00 termina a string.
  - 0x0A = quebra de linha. Outros bytes < 0x20 sao codigos de controle
    (ex.: 0x05, 0x08, 0x09, 0x0C, 0x0F, 0x10).
  - 0x87 XX = icone (word 0x87XX), preservado como token {ICON:XX}.
  - As strings sao referenciadas por tabelas de ponteiros absolutos
    (word LE = 0x08000000 + offset no ROM).

FF2 (FINAL FANTASY II - script principal):
  - Codigos de 16 bits little-endian, pagina de glifos propria:
      0x00-0x09 = '0'-'9'      0x0A-0x23 = 'A'-'Z'
      0x24-0x3D = 'a'-'z'      0x80F9 = espaco
      0x40 ',' 0x41 '.' 0x43 ';' 0x44 '?' 0x45 '!' 0x4C '\'' 0x4E '"'
      0xFB '-' 0xFF '-' 0xF8 '/' 0x0100 '~'
      0x80F0 = quebra de linha  0x80FF = terminador
  - Tabela de 4256 ponteiros absolutos em 0x2601C0; strings contiguas em
    0x264440-0x295E7E.
  - CUIDADO: a tabela aponta para um POOL DE LINHAS/FRAGMENTOS individuais,
    ordenado por sufixo e deduplicado - nao para mensagens completas em ordem
    de historia. Uma fala em jogo e a concatenacao de varias entradas
    consecutivas. Traduza entrada a entrada (preserva contagem/ordem); a
    concordancia entre linhas vizinhas pode ficar imperfeita.
  - Rotulos/eventos de 2 linhas ja contem 0x80F0 e devem ser traduzidos como
    bloco, preservando o centro original quando forem centralizados.

Reinsercao
----------
Modo padrao (`insert`): todas as strings referenciadas por tabela sao
realocadas para o espaco livre (0xEE0760-0x01000000, preenchido com 0xFF) e os
ponteiros sao atualizados. As strings originais ficam intactas.

Modo compacto (`insert-packed`): as traducoes sao reempacotadas dentro dos
proprios slots de texto originais (antes de 0xEE0760) e os ponteiros sao
atualizados. Nada e escrito no espaco livre do fim da ROM. E util para
aparelhos/copias que truncam ou ignoram o final do arquivo; em troca, o texto
original dos slots reutilizados e sobrescrito (os slots de entradas nao
traduzidas sao preservados).
No modo padrao, o texto original permanece intacto no ROM, portanto qualquer
referencia nao mapeada continua apontando para texto valido (no pior caso, uma
linha fica em ingles) - nunca para dados corrompidos. No modo compacto, os
slots reutilizados sao sobrescritos; referencias rigidas nao mapeadas para o
meio desses slots podem exibir outro texto.

Uso
---
  python3 ff12dos_text.py extract --rom X.gba --out-dir DIR
  python3 ff12dos_text.py insert --rom X.gba --manifest DIR/manifest.json \
      --csv DIR/ff1.csv DIR/ff2.csv --out NOVO.gba
  python3 ff12dos_text.py verify --rom NOVO.gba --manifest DIR/manifest.json

Dependencias: apenas biblioteca padrao.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import struct
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Constantes do jogo
# ---------------------------------------------------------------------------

GBA_BASE = 0x08000000
FREE_SPACE = 0x00EE0760          # inicio da area 0xFF no fim do ROM
ROM_SIZE = 0x01000000

# (offset da tabela, nome, numero de entradas)
FF1_TABLES = [
    (0x00040304, "ff1_locations", 25),
    (0x0019E650, "ff1_items", 651),
    (0x001A1650, "ff1_spells", 204),
    (0x001A3E84, "ff1_menu_terms", 221),
    (0x001A4344, "ff1_black_magic", 20),
    (0x001A4470, "ff1_white_magic", 20),
    (0x001A4D0C, "ff1_key_items", 15),
    (0x001A5030, "ff1_ui", 56),
    (0x001BE32C, "ff1_map_names", 34),
    (0x001DC9F8, "ff1_elements", 15),
    (0x001DDD38, "ff1_bestiary_a", 195),
    (0x00210370, "ff1_dialogue", 2560),
    (0x00215CAC, "ff1_bestiary_b", 195),
    (0x002267A4, "ff1_bestiary_c", 195),
    (0x0022D0D8, "ff1_bestiary_d", 195),
    (0x002331A0, "ff1_monster_names", 169),
    (0x00EDF15C, "ff1_config", 29),
    (0x00EDF1FC, "ff1_menu_labels", 27),
    (0x00EDF6C0, "ff1_ending", 61),
]

# Tabelas detectadas automaticamente mas que NAO contem texto traduzivel:
#  0x1DA25C  dados de fonte/grafico (nao decodifica)
#  0x216F70 / 0x2369EC / 0x238814 / 0x2388D8 / 0x25A954 / 0x2965DC
#            tabelas de opcoes internas (apenas codigos de controle)
#  0xEDF7B8  menu de debug em japones ("message display")
SKIP_TABLES = {
    0x001DA25C, 0x00216F70, 0x002369EC, 0x00238814,
    0x002388D8, 0x0025A954, 0x002965DC,
    0x00EDF7B8,
}

FF2_PTR_TABLE = 0x002601C0
FF2_PTR_COUNT = 4256
FF2_STR_LO = 0x00264440
FF2_STR_HI = 0x00295E80

# ---------------------------------------------------------------------------
# FF1 - Shift-JIS
# ---------------------------------------------------------------------------

def _sjis_char(b1: int, b2: int):
    """Decodifica um par SJIS usado pelo jogo (None se invalido)."""
    if b1 == 0x87:                      # icone
        return chr(0xE000 + b2)
    if not (0x81 <= b1 <= 0x84):
        return None
    if not (0x40 <= b2 <= 0x7E or 0x80 <= b2 <= 0xFC):
        return None
    try:
        return bytes([b1, b2]).decode("cp932")
    except UnicodeDecodeError:
        return None


def decode_ff1(data: bytes, off: int):
    """Decodifica string FF1. Retorna (texto_display, offset_fim) ou (None, None).

    O fluxo mistura SJIS de 2 bytes (texto normal, formas fullwidth) com
    ASCII de 1 byte (especificadores de formato como %0, %2d, %s).
    """
    out = []
    j = off
    n = len(data)
    while j < n:
        b = data[j]
        if b == 0:
            return "".join(out), j
        if b < 0x20:
            out.append("\n" if b == 0x0A else "{CTL:%02X}" % b)
            j += 1
            continue
        if b < 0x80:                       # ASCII de 1 byte
            out.append(chr(b))
            j += 1
            continue
        if j + 1 >= n:
            return None, None
        c = _sjis_char(b, data[j + 1])
        if c is None:
            return None, None
        out.append(c)
        j += 2
    return None, None


# Especificadores de formato expandidos pelo motor (ficam em ASCII de 1 byte).
FMT_RE = re.compile(r"%(?:\d+[ds]?|[ds])")
TOKEN_RE = re.compile(r"\{(?:CTL|ICON|FMT|C):[^}]*\}")

# Equivalencias tipograficas (NFKC nao converte aspas curvas nem travessoes)
_UNICODE_EQ = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u00b4": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2015": "-", "\u2212": "-", "\u00ad": "", "\u00a0": " ",
    "\u2026": "...", "\u2032": "'", "\u2033": '"', "\u00b7": " ",
})


def _display_ff1(raw: str) -> str:
    """Converte a forma fullwidth para ASCII legivel, preservando tokens."""
    out = []
    i = 0
    while i < len(raw):
        if raw[i] == "{":
            j = raw.find("}", i)
            if j > 0:
                out.append(raw[i:j + 1])
                i = j + 1
                continue
        if 0xE000 <= ord(raw[i]) <= 0xF0FF:      # icone
            out.append("{ICON:%02X}" % (ord(raw[i]) - 0xE000))
            i += 1
            continue
        out.append(raw[i])
        i += 1
    text = unicodedata.normalize("NFKC", "".join(out))
    # tokeniza %0/%1/%2/%2d/%s/%d
    return FMT_RE.sub(lambda m: "{FMT:%s}" % m.group(0), text)


def _split_tokens(text: str):
    """Divide o texto em (eh_token, trecho)."""
    parts = []
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            parts.append((False, text[pos:m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    if pos < len(text):
        parts.append((False, text[pos:]))
    return parts


def _map_text(text: str, table, reps, unsupported_to=""):
    text = text.translate(_UNICODE_EQ)
    out = []
    for ch in text:
        if ch in reps:
            out.append(reps[ch])
        elif ch in table or ch == "\n":
            out.append(ch)
        else:
            base = unicodedata.normalize("NFD", ch)
            base = "".join(c for c in base if not unicodedata.combining(c))
            if base in table or base in reps:
                out.append(reps.get(base, base))
            else:
                out.append(unsupported_to)
    return "".join(out)


# ASCII -> forma fullwidth realmente presente no ROM.
_FF1_MAP = {chr(c): chr(0xFF01 + (c - 0x21)) for c in range(0x21, 0x7F)}
_FF1_MAP.update({
    " ": "\u3000",   # espaco ideografico (unico espaco usado pelo jogo)
    '"': "\u201D",
    "'": "\u2019",
    "`": "\u2019",
    ";": "\uFF0C",   # o ROM nao usa ';' -> virgula
    "-": "\uFF0D",
})

_FF1_REPS = {
    "(": "", ")": "", "[": "", "]": "", "{": "", "}": "", "<": "", ">": "",
    "|": "", "\\": "", "@": "", "#": "", "$": "", "%": " por cento",
    "^": "", "&": " e ", "_": " ", "=": " - ", "+": " e ", "~": "-",
    "*": "", "\u2026": "...", "\u2014": "-", "\u2013": "-", "\t": " ",
}


def sanitize_ff1(text: str) -> str:
    """Ajusta texto ASCII para o conjunto de glifos disponivel no FF1."""
    text = unicodedata.normalize("NFKC", text)
    out = []
    for is_tok, part in _split_tokens(text):
        if is_tok:
            out.append(part)
        else:
            out.append(_map_text(part, _FF1_MAP, _FF1_REPS))
    return "".join(out)


def encode_ff1(text: str) -> bytes:
    """Codifica texto (formato do CSV) para bytes FF1 terminados em 0x00."""
    text = sanitize_ff1(text)
    out = bytearray()
    for is_tok, part in _split_tokens(text):
        if is_tok:
            if part.startswith("{CTL:"):
                out.append(int(part[5:-1], 16))
            elif part.startswith("{ICON:"):
                out += bytes([0x87, int(part[6:-1], 16)])
            elif part.startswith("{FMT:"):
                out += part[5:-1].encode("ascii")
            continue
        for ch in part:
            if ch == "\n":
                out.append(0x0A)
                continue
            mapped = _FF1_MAP.get(ch, ch)
            try:
                out += mapped.encode("cp932")
            except UnicodeEncodeError as exc:
                raise ValueError("caractere sem glifo FF1: %r (%s)" % (ch, exc))
    out.append(0x00)
    return bytes(out)



# ---------------------------------------------------------------------------
# FF2 - pagina de glifos de 16 bits
# ---------------------------------------------------------------------------

_FF2_ENC = {}
_FF2_DEC = {}
for _c in range(0x0A, 0x24):
    _FF2_ENC[chr(_c + 0x37)] = _c
    _FF2_DEC[_c] = chr(_c + 0x37)
for _c in range(0x24, 0x3E):
    _FF2_ENC[chr(_c + 0x3D)] = _c
    _FF2_DEC[_c] = chr(_c + 0x3D)
for _c in range(0x00, 0x0A):
    _FF2_ENC[chr(_c + 0x30)] = _c
    _FF2_DEC[_c] = chr(_c + 0x30)
_FF2_ENC.update({
    " ": 0x80F9, "\n": 0x80F0, ",": 0x40, ".": 0x41, ";": 0x43, "?": 0x44,
    "!": 0x45, "'": 0x4C, '"': 0x4E, "-": 0xFB, "\u2014": 0xFF, "/": 0xF8,
    "~": 0x0100,
})
_FF2_DEC.update({
    0x80F9: " ", 0x80F0: "\n", 0x80FF: "", 0x40: ",", 0x41: ".", 0x43: ";",
    0x44: "?", 0x45: "!", 0x4C: "'", 0x4E: '"', 0xFB: "-", 0xFF: "-",
    0xF8: "/", 0x0100: "~",
})


def decode_ff2(data: bytes, off: int):
    out = []
    j = off
    n = len(data)
    while j + 1 < n:
        w = data[j] | (data[j + 1] << 8)
        j += 2
        if w == 0x80FF:
            return "".join(out), j
        if w in _FF2_DEC:
            out.append(_FF2_DEC[w])
        else:
            out.append("{C:%X}" % w)
    return None, None


_FF2_REPS = {
    "(": "", ")": "", "[": "", "]": "", "{": "", "}": "", "<": "", ">": "",
    "|": "", "\\": "/", "@": "", "#": "", "$": "", "%": "", "^": "",
    "&": " e ", "=": "-", "+": " e ", "_": " ", "*": "", "\t": " ",
    "\u2026": "...", "\u2014": "-", "\u2013": "-", ":": ",", "\u00b7": " ",
}

def sanitize_ff2(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    out = []
    for is_tok, part in _split_tokens(text):
        if is_tok:
            out.append(part)
        else:
            out.append(_map_text(part, _FF2_ENC, _FF2_REPS))
    return "".join(out)


def encode_ff2(text: str) -> bytes:
    text = sanitize_ff2(text)
    out = bytearray()
    for is_tok, part in _split_tokens(text):
        if is_tok:
            if part.startswith("{C:"):
                out += struct.pack("<H", int(part[3:-1], 16))
            continue
        for ch in part:
            code = _FF2_ENC.get(ch)
            if code is not None:
                out += struct.pack("<H", code)
    out += struct.pack("<H", 0x80FF)
    return bytes(out)



# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------

class Table:
    def __init__(self, offset, name, count, encoding):
        self.offset = offset
        self.name = name
        self.count = count
        self.encoding = encoding

    @property
    def decode(self):
        return decode_ff1 if self.encoding == "ff1" else decode_ff2

    def entries(self, data):
        for i in range(self.count):
            site = self.offset + 4 * i
            v = struct.unpack_from("<I", data, site)[0]
            if not (GBA_BASE <= v < GBA_BASE + ROM_SIZE):
                yield i, site, None
                continue
            yield i, site, v - GBA_BASE


def tables():
    out = [Table(o, n, c, "ff1") for o, n, c in FF1_TABLES]
    out.append(Table(FF2_PTR_TABLE, "ff2_script", FF2_PTR_COUNT, "ff2"))
    return out


def extract(data: bytes):
    """Retorna (entries, skipped). Cada entry e um dict serializavel."""
    entries = []
    skipped = []
    for tbl in tables():
        skip = tbl.offset in SKIP_TABLES
        bad = 0
        for idx, site, target in tbl.entries(data):
            if target is None:
                bad += 1
                skipped.append({"table": tbl.name, "index": idx, "reason": "ponteiro invalido"})
                continue
            text, end = tbl.decode(data, target)
            if text is None:
                bad += 1
                skipped.append({"table": tbl.name, "index": idx, "offset": target,
                                "reason": "falha ao decodificar"})
                continue
            disp = _display_ff1(text) if tbl.encoding == "ff1" else text
            note = ""
            if skip:
                note = "tabela interna (nao traduzir)"
            entries.append({
                "id": "%s:%06X:%04d" % (tbl.encoding, tbl.offset & 0xFFFFFF, idx),
                "table": tbl.name,
                "table_offset": tbl.offset,
                "index": idx,
                "ptr_site": site,
                "rom_offset": target,
                "encoding": tbl.encoding,
                "text": disp,
                "skip": skip or not disp.strip(),
                "note": note,
            })
        if bad:
            print("  ! %s: %d entradas invalidas" % (tbl.name, bad), file=sys.stderr)
    return entries, skipped


def _wrap(text: str, widths):
    """Requebra texto usando as larguras de linha originais como capacidade."""
    words = text.split()
    if not words or not widths:
        return text
    lines = []
    cur = ""
    cap_i = 0
    for w in words:
        cap = widths[min(cap_i, len(widths) - 1)]
        cand = w if not cur else cur + " " + w
        if len(cand) <= cap or not cur:
            cur = cand
        else:
            lines.append(cur)
            cap_i += 1
            cur = w
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def insert(data: bytes, manifest, translations):
    """Gera novo ROM com as strings traduzidas realocadas no espaco livre."""
    out = bytearray(data)
    free = FREE_SPACE
    cache = {}
    used = 0
    missing = 0
    for entry in manifest["entries"]:
        tr = translations.get(entry["id"])
        if tr is None or entry.get("skip"):
            continue
        tr = tr.strip("\n")
        enc = entry["encoding"]
        key = (enc, tr)
        if key in cache:
            off = cache[key]
        else:
            raw = encode_ff1(tr) if enc == "ff1" else encode_ff2(tr)
            off = free
            while off % 4:
                off += 1
            end = off + len(raw)
            if end > ROM_SIZE:
                raise SystemExit("espaco livre esgotado em 0x%08X" % free)
            out[off:end] = raw
            free = end
            cache[key] = off
            used += len(raw)
        struct.pack_into("<I", out, entry["ptr_site"], GBA_BASE + off)
    if free >= ROM_SIZE:
        raise SystemExit("ROM sem espaco livre")
    print("  reinserido: %d bytes unicos, %d strings, espaco livre restante: %d bytes"
          % (used, len(cache), ROM_SIZE - ((free + 3) & ~3)))
    return bytes(out), free


def insert_packed(data: bytes, manifest, translations):
    """Reempacota as traducoes nos slots de texto originais (antes do espaco livre).

    Nenhum byte e escrito em [FREE_SPACE, ROM_SIZE) e nenhum ponteiro aponta
    para la. Todos os bytes reutilizados pertencem a strings de entradas que
    serao traduzidas; bytes de entradas nao traduzidas (ou skip) sao
    preservados e ficam fora dos intervalos usados.

    Retorna (rom_bytes, stats). Levanta SystemExit se a compactacao nao couber.
    """
    out = bytearray(data)
    limit = FREE_SPACE

    def original_range(entry):
        off = entry["rom_offset"]
        if entry["encoding"] == "ff1":
            _, end = decode_ff1(data, off)
            if end is None:
                return None
            return off, end - off + 1
        _, end = decode_ff2(data, off)
        if end is None:
            return None
        return off, end - off

    # Marca byte a byte o que pode ser sobrescrito. Um byte coberto por uma
    # entrada nao traduzida nunca e reutilizado.
    cov_t = bytearray(limit)
    cov_u = bytearray(limit)
    for entry in manifest["entries"]:
        r = original_range(entry)
        if r is None:
            continue
        off, ln = r
        if off >= limit:
            continue
        end = min(off + ln, limit)
        if end <= off:
            continue
        translated = entry["id"] in translations and not entry.get("skip")
        arr = cov_t if translated else cov_u
        arr[off:end] = b"\x01" * (end - off)

    usable = bytearray(1 if cov_t[i] and not cov_u[i] else 0 for i in range(limit))
    runs = []
    i = 0
    while i < limit:
        if usable[i]:
            j = i
            while j < limit and usable[j]:
                j += 1
            runs.append([i, j - i, 0])       # inicio, capacidade, usado
            i = j
        else:
            i += 1

    # Uma chave por sequencia codificada; varias entradas podem compartilhar.
    items = {}
    for entry in manifest["entries"]:
        if entry["id"] not in translations or entry.get("skip"):
            continue
        text = translations[entry["id"]].strip("\n")
        enc = entry["encoding"]
        raw = encode_ff1(text) if enc == "ff1" else encode_ff2(text)
        items.setdefault((enc, raw), []).append(entry)

    bins = sorted(runs, key=lambda b: b[1], reverse=True)
    placement = {}
    failed = []
    for key in sorted(items, key=lambda k: len(k[1]), reverse=True):
        size = len(key[1])
        # FF2 usa glifos de 16 bits: o inicio precisa ser par, como no pool
        # original. FF1 e byte a byte e pode ficar em qualquer offset.
        align = 2 if key[0] == "ff2" else 1
        for b in bins:
            start = b[0] + b[2]
            pad = (-start) % align
            if b[2] + pad + size <= b[1]:
                placement[key] = start + pad
                b[2] += pad + size
                break
        else:
            failed.append((size, key[0]))
    if failed:
        raise SystemExit("compactacao impossivel: %d itens, %d bytes"
                         % (len(failed), sum(s for s, _ in failed)))

    ptr_updates = 0
    last = 0
    for key, off in placement.items():
        raw = key[1]
        out[off:off + len(raw)] = raw
        last = max(last, off + len(raw))
        for entry in items[key]:
            struct.pack_into("<I", out, entry["ptr_site"], GBA_BASE + off)
            ptr_updates += 1

    if any(x != 0xFF for x in out[FREE_SPACE:]):
        raise SystemExit("espaco livre foi alterado")
    stats = {
        "items": len(items),
        "bytes": sum(len(k[1]) for k in items),
        "capacity": sum(b[1] for b in bins),
        "runs": len(bins),
        "used_runs": sum(1 for b in bins if b[2]),
        "ptr_updates": ptr_updates,
        "last": last,
    }
    print("  compactado: %d bytes unicos, %d strings, %d ponteiros, ultimo byte 0x%X"
          % (stats["bytes"], stats["items"], stats["ptr_updates"], stats["last"]))
    return bytes(out), stats


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

CSV_HEADER = ["id", "original", "traducao", "status", "nota"]
_STATUS_PENDING = "pendente"


def write_csv(path, entries, keep_translation=None):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_HEADER)
        for e in entries:
            tr = e.get("traducao", "")
            if keep_translation:
                tr = keep_translation.get(e["id"], tr)
            status = e.get("status") or (_STATUS_PENDING if not e["skip"] else "ignorado")
            w.writerow([e["id"], e["text"], tr, status, e.get("note", "")])


def read_csv(path):
    rows = {}
    status = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if not row.get("id"):
                continue
            rows[row["id"]] = row.get("traducao") or ""
            status[row["id"]] = (row.get("status") or "").strip().lower()
    return rows, status


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="extrai textos para CSV + manifest")
    e.add_argument("--rom", required=True)
    e.add_argument("--out-dir", required=True)

    i = sub.add_parser("insert", help="reinsere traducoes e gera ROM novo")
    i.add_argument("--rom", required=True)
    i.add_argument("--manifest", required=True)
    i.add_argument("--csv", nargs="+", required=True)
    i.add_argument("--out", required=True)

    ip = sub.add_parser("insert-packed",
                        help="reinsere traducoes nos slots originais (sem usar o fim da ROM)")
    ip.add_argument("--rom", required=True)
    ip.add_argument("--manifest", required=True)
    ip.add_argument("--csv", nargs="+", required=True)
    ip.add_argument("--out", required=True)

    v = sub.add_parser("verify", help="re-extrai o ROM gerado e compara com os CSVs")
    v.add_argument("--rom", required=True)
    v.add_argument("--manifest", required=True)
    v.add_argument("--csv", nargs="+", required=True)

    a = ap.parse_args(argv)
    data = open(a.rom, "rb").read()

    if a.cmd == "extract":
        os.makedirs(a.out_dir, exist_ok=True)
        entries, skipped = extract(data)
        with open(os.path.join(a.out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump({"rom": os.path.basename(a.rom), "size": len(data),
                       "free_space": FREE_SPACE, "entries": entries,
                       "skipped": skipped}, fh, indent=1, ensure_ascii=False)
        for enc in ("ff1", "ff2"):
            rows = [x for x in entries if x["encoding"] == enc]
            write_csv(os.path.join(a.out_dir, enc + ".csv"), rows)
            print("  %s.csv: %d linhas (%d ignoradas)" %
                  (enc, len(rows), sum(1 for r in rows if r["skip"])))
        print("  manifest.json: %d entradas, %d ignoradas na extracao"
              % (len(entries), len(skipped)))
        return 0

    manifest = json.load(open(a.manifest, encoding="utf-8"))
    trans = {}
    for path in a.csv:
        rows, status = read_csv(path)
        for k, v in rows.items():
            if v and status.get(k, "") not in ("ignorado", "adiado"):
                trans[k] = v
    print("  traducoes carregadas: %d" % len(trans))

    if a.cmd == "insert":
        new, free = insert(data, manifest, trans)
        with open(a.out, "wb") as fh:
            fh.write(new)
        print("  ROM gerado: %s (%d bytes)" % (a.out, len(new)))
        return 0

    if a.cmd == "insert-packed":
        new, stats = insert_packed(data, manifest, trans)
        with open(a.out, "wb") as fh:
            fh.write(new)
        print("  ROM gerado: %s (%d bytes)" % (a.out, len(new)))
        return 0

    if a.cmd == "verify":
        entries, _ = extract(data)
        by_id = {e["id"]: e for e in entries}

        def norm(s):
            return " ".join(unicodedata.normalize("NFKC", s.translate(_UNICODE_EQ)).split())

        ok = bad = 0
        for k, v in trans.items():
            e = by_id.get(k)
            if not e:
                bad += 1
                print("  ! id ausente: %s" % k)
                continue
            expected = sanitize_ff1(v) if e["encoding"] == "ff1" else sanitize_ff2(v)
            got = e["text"]
            if norm(got) == norm(expected):
                ok += 1
            else:
                bad += 1
                if bad <= 10:
                    print("  ! %s\n      esperado: %r\n      obtido:   %r" % (k, expected, got))
        print("  verificacao: %d ok, %d divergentes" % (ok, bad))
        return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
