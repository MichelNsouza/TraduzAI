#!/usr/bin/env python3
"""
propósito: Decodificar/gerar CSV a partir de arquivo .TBL genérico (tabela de caracteres)
como usar: python3 workspace/scripts/tbl_decode.py --tbl tabela.tbl --bin arquivo.bin --out saida.csv [--start 0x1000] [--end 0x2000]
dependências: python3 (stdlib)
como generalizar: Totalmente genérico - carrega qualquer arquivo .TBL no formato "XX=char" ou "XXXX=char", não tem hardcode de jogo
"""
import argparse
import csv
import os
from pathlib import Path


def load_tbl(tbl_path):
    tbl = {}
    with open(tbl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip()
                # try hex
                try:
                    if len(key) == 2:
                        tbl[int(key, 16)] = val
                    elif len(key) == 4:
                        tbl[int(key, 16)] = val
                    else:
                        # try as-is
                        try:
                            tbl[int(key, 16)] = val
                        except:
                            pass
                except ValueError:
                    pass
    return tbl


def decode_string(data, offset, tbl, maxlen=200):
    out = []
    i = offset
    count = 0
    while i < len(data) and count < maxlen:
        # try 2-byte first
        if i + 1 < len(data):
            b2 = (data[i] << 8) | data[i+1]
            if b2 in tbl:
                out.append(tbl[b2])
                i += 2
                count += 1
                if tbl[b2] == '\n' or tbl[b2] == '\x00':
                    break
                continue
        # try 1-byte
        b1 = data[i]
        if b1 in tbl:
            out.append(tbl[b1])
            i += 1
            count += 1
            if tbl[b1] == '\n' or tbl[b1] == '\x00':
                break
            continue
        # unknown
        break
    return ''.join(out), i - offset


def main():
    p = argparse.ArgumentParser(description='Generic TBL decoder')
    p.add_argument('--tbl', required=True, help='Path to .TBL file')
    p.add_argument('--bin', required=True, help='Binary file to scan')
    p.add_argument('--out', required=True, help='Output CSV')
    p.add_argument('--start', type=lambda x: int(x,0), default=0)
    p.add_argument('--end', type=lambda x: int(x,0), default=None)
    args = p.parse_args()
    
    tbl = load_tbl(args.tbl)
    with open(args.bin, 'rb') as f:
        data = f.read()
    
    start = args.start
    end = args.end if args.end is not None else len(data)
    
    results = []
    idx = 0
    i = start
    while i < end:
        s, consumed = decode_string(data, i, tbl)
        if len(s.strip()) >= 2:
            results.append({
                'id': f'STR_{idx:05d}',
                'original': s,
                'traducao': '',
                'status': 'pendente',
                'nota': f'offset:{i:08X}'
            })
            idx += 1
            i += consumed if consumed > 0 else 1
            continue
        i += 1
    
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id','original','traducao','status','nota'])
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f'Extracted {len(results)} strings to {args.out}')


if __name__ == '__main__':
    main()
