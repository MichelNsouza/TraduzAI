#!/usr/bin/env python3
"""Reaplica o layout (quebras de linha/centralizacao) do original sobre a traducao.

Proposito
    Depois de traduzir, alinhar a traducao as larguras de linha do texto
    original (inclusive centralizacao por espacos a esquerda) sem traduzir
    de novo. Util quando a traducao foi produzida por outro motor ou editada
    a mao.

Como usar
    python3 relayout_csv.py --csv a.csv b.csv --out-dir saida/

    Gera os mesmos arquivos em --out-dir (ou sobrescreve com --in-place).

Dependencias
    apenas biblioteca padrao (reutiliza translate_csv_argos.layout).

Como generalizar
    Nenhum detalhe de jogo: opera sobre as colunas original/traducao.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate_csv_argos import layout  # noqa: E402

CSV_HEADER = ["id", "original", "traducao", "status", "nota"]


def reflow(original, translated):
    if not translated or "\n" not in original:
        return translated
    parts = original.split("\n")
    # apenas as linhas de conteudo da traducao (o layout reconstroi os brancos)
    trans_content = [l for l in translated.split("\n") if l.strip()]
    out = []
    i = 0
    ti = 0
    while i < len(parts):
        if not parts[i].strip():
            out.append("")
            i += 1
            continue
        j = i
        while j < len(parts) and parts[j].strip():
            j += 1
        group_orig = parts[i:j]
        group_tr = trans_content[ti:ti + len(group_orig)] or [""]
        ti += len(group_tr)
        text = " ".join(l.strip() for l in group_tr if l.strip())
        out.append(layout("\n".join(group_orig), text))
        i = j
    if ti < len(trans_content):
        out.extend(trans_content[ti:])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", nargs="+", required=True)
    ap.add_argument("--out-dir")
    ap.add_argument("--in-place", action="store_true")
    a = ap.parse_args(argv)
    for path in a.csv:
        rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
        changed = 0
        for r in rows:
            new = reflow(r.get("original", ""), r.get("traducao", ""))
            if new != r.get("traducao", ""):
                r["traducao"] = new
                changed += 1
        dst = path if a.in_place else os.path.join(a.out_dir or ".", os.path.basename(path))
        if not a.in_place:
            os.makedirs(a.out_dir or ".", exist_ok=True)
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_HEADER)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in CSV_HEADER})
        print("  %s: %d linhas re-layoutadas" % (dst, changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
