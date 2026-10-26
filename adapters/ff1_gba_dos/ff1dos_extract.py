#!/usr/bin/env python3
import struct
import csv
import os
import sys

ROM = sys.argv[1] if len(sys.argv) > 1 else '/home/michel/projetos/TraduzAI-develop/workspace/extracted/ff1ff2dos_gba/rom_original.gba'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/michel/projetos/TraduzAI-develop/workspace/reports/ff1dos_texts.csv'

# Decoding based on Jeff Ludwig's notes
DECODE = {}
# Letters A-Z a-z
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    DECODE[0x8260 + i] = c
for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
    DECODE[0x8281 + i] = c
# Numbers
for i in range(10):
    DECODE[0x824f + i] = str(i)
# Symbols
sym = {
    0x8140: ' ',
    0x8143: ',',
    0x8144: '.',
    0x8146: ':',
    0x8147: ';',
    0x8148: '?',
    0x8149: '!',
    0x8151: '_',
    0x815e: '/',
    0x8166: "'",
    0x817c: '-',
    0x8193: '%',
    0x810a: '\n',
}
DECODE.update(sym)
# Item icons/special (just label them)
DECODE[0x8740] = '[Sword]'
DECODE[0x8742] = '[Knife]'
DECODE[0x8743] = '[Nunchaku]'
DECODE[0x8746] = '[Staff]'
DECODE[0x8747] = '[Robe]'
DECODE[0x8749] = '[Armlet]'
DECODE[0x874c] = '[Gloves]'
DECODE[0x874d] = '[White]'
DECODE[0x874e] = '[Black]'
DECODE[0x874f] = '[Potion]'
DECODE[0x8750] = '[Bag]'

def decode_string(data, off):
    res = []
    i = off
    while i + 1 < len(data):
        b = data[i] | (data[i+1] << 8)
        if b == 0x0000:
            break
        if b in DECODE:
            res.append(DECODE[b])
        else:
            # try to see if it's a control code or unknown
            # print unknown as hex for now
            res.append(f'\\x{b:04X}')
        i += 2
        if len(res) > 500:  # safety
            break
    return ''.join(res), i - off

def main():
    with open(ROM, 'rb') as f:
        data = f.read()
    
    results = []
    idx = 0
    
    # Known ranges from notes
    ranges = [
        ('ClassNames1', 0x1da85c, 0x1da937),
        ('ClassNames2', 0x1e08a4, 0x1e097f),
        ('ClassNames3', 0x1e13b4, 0x1e148f),
        ('ItemNames', 0x19a261, 0x19a659),
        ('WeaponNames', 0x19a65a, 0x19ac05),
        ('ArmorNames', 0x19ac06, 0x19b319),
        ('QuestItemDesc', 0x19ac1a, 0x19bc9e),
        ('ItemDesc', 0x19bc9f, 0x19c40c),
        ('WeaponDesc', 0x19c40d, 0x19d454),
        ('SpellNames1', 0x1a8668, None),
        ('SpellNames2', 0x1a021d, None),
        ('SpellDesc', 0x1a0787, 0x1a164e),
        ('MonsterAttacks', 0x1a05bb, 0x1a0786),
    ]
    
    for name, start, end in ranges:
        if end is None:
            end = start + 0x2000  # scan chunk
        # scan through range for strings
        i = start
        while i < end:
            b = data[i] | (data[i+1] << 8) if i+1 < len(data) else 0
            # look for start of string (letter or symbol we know)
            if b in DECODE or (b >= 0x8260 and b <= 0x829a) or (b >= 0x824f and b <= 0x8258):
                s, consumed = decode_string(data, i)
                if len(s.strip()) >= 2:  # meaningful string
                    results.append({
                        'id': f'{name}_{idx:05d}',
                        'original': s,
                        'traducao': '',
                        'status': 'pendente',
                        'nota': f'offset:{i:08X}'
                    })
                    idx += 1
                    i += consumed if consumed > 0 else 2
                    continue
            i += 2
    
    # Write CSV
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'original', 'traducao', 'status', 'nota'])
        w.writeheader()
        for r in results:
            w.writerow(r)
    
    print(f'Extracted {len(results)} strings to {OUT}')

if __name__ == '__main__':
    main()
