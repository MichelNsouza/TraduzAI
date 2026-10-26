#!/usr/bin/env python3
import csv
import os
import sys

ROM = sys.argv[1]
OUT = sys.argv[2]

with open(ROM, 'rb') as f:
    data = f.read()

# Build decode table from Jeff Ludwig's notes
dec = {}
# Uppercase A-Z
for i in range(26):
    dec[0x8260 + i] = chr(ord('A') + i)
# Lowercase a-z  
for i in range(26):
    dec[0x8281 + i] = chr(ord('a') + i)
# Numbers
for i in range(10):
    dec[0x824f + i] = str(i)
# Punctuation
dec[0x8140] = ' '
dec[0x8143] = ','
dec[0x8144] = '.'
dec[0x8146] = ':'
dec[0x8147] = ';'
dec[0x8148] = '?'
dec[0x8149] = '!'
dec[0x8151] = '_'
dec[0x815e] = '/'
dec[0x8166] = "'"
dec[0x817c] = '-'
dec[0x8193] = '%'
dec[0x810a] = '\n'
dec[0x8160] = ' '
# Some others
dec[0x827C] = ','  # sometimes appears

# Item icons
dec[0x8740] = '[Sword]'
dec[0x8742] = '[Knife]'
dec[0x8743] = '[Nunchaku]'
dec[0x8746] = '[Staff]'
dec[0x8747] = '[Robe]'
dec[0x8749] = '[Armlet]'
dec[0x874c] = '[Gloves]'
dec[0x874d] = '[White Magic]'
dec[0x874e] = '[Black Magic]'
dec[0x874f] = '[Potion]'
dec[0x8750] = '[Bag]'

def decode(data, start, maxlen=200):
    out = []
    i = start
    count = 0
    while i + 1 < len(data) and count < maxlen:
        b = data[i] | (data[i+1] << 8)
        if b == 0x0000:
            break
        if b in dec:
            out.append(dec[b])
        elif b >= 0x8260 and b <= 0x8279:  # A-Z
            out.append(chr(ord('A') + (b - 0x8260)))
        elif b >= 0x8281 and b <= 0x829a:  # a-z
            out.append(chr(ord('a') + (b - 0x8281)))
        elif b >= 0x824f and b <= 0x8258:  # 0-9
            out.append(chr(ord('0') + (b - 0x824f)))
        else:
            # skip unknown control codes or show placeholder
            out.append(f'[{b:04X}]')
        i += 2
        count += 1
    return ''.join(out), i - start

# Try to find all text blocks by scanning for pointer tables and strings
results = []
seen = set()

# Scan known areas more directly
# Item/weapon/armor names are often contiguous
areas = [
    (0x19a261, 0x19b400, 'Items'),
    (0x19b400, 0x19d500, 'ItemWeapArmorDesc'),
    (0x1a021d, 0x1a2000, 'Magic'),
    (0x1da85c, 0x1da940, 'Class'),
    (0x1e08a4, 0x1e09b0, 'Class2'),
    (0x1e13b0, 0x1e14a0, 'Class3'),
    (0x2257ac, 0x226000, 'Monsters'),
]

idx = 0
for start, end, label in areas:
    i = start
    while i < end - 2:
        b = data[i] | (data[i+1] << 8)
        # Check if looks like start of string
        if (b >= 0x8260 and b <= 0x829a) or (b >= 0x824f and b <= 0x8258) or b in [0x8140, 0x8740, 0x8742, 0x8743, 0x8746, 0x8747]:
            s, consumed = decode(data, i)
            if len(s) >= 3 and not any(x in s for x in ['[', ']']) or (s and any(c.isalnum() for c in s)):
                # filter out garbage
                clean = s.replace('[', '').replace(']', '')
                if len(clean.strip()) >= 2:
                    key = (i, clean)
                    if key not in seen:
                        seen.add(key)
                        results.append({
                            'id': f'{label}_{idx:05d}',
                            'original': clean,
                            'traducao': '',
                            'status': 'pendente',
                            'nota': f'raw:{s[:40]}@{i:08X}'
                        })
                        idx += 1
            i += consumed if consumed >= 2 else 2
            continue
        i += 1

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['id', 'original', 'traducao', 'status', 'nota'])
    w.writeheader()
    for r in results:
        w.writerow(r)

print(f'Extracted {len(results)} strings')
