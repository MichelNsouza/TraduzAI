#!/usr/bin/env python3
"""Aplica a pos-edicao PT-BR sobre a coluna traducao de um CSV ja traduzido.

Proposito
    Corrigir formas de portugues europeu (ou aplicar o glossario) sem
    retraduzir. Nao altera quebras de linha nem indentacao.

Como usar
    python3 postedit_csv.py --csv traducao/ff1.csv --glossary glossary.json
    # grava em --out-dir (ou sobrescreve com --in-place)

Dependencias
    apenas biblioteca padrao
    (reutiliza PTBR_RULES/post_edit de translate_csv_argos.py)

Como generalizar
    Nenhum detalhe de jogo; as regras sao de idioma (PT-PT -> PT-BR).
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translate_csv_argos import CSV_HEADER, load_glossary, post_edit  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", nargs="+", required=True)
    ap.add_argument("--glossary")
    ap.add_argument("--out-dir")
    ap.add_argument("--in-place", action="store_true")
    a = ap.parse_args(argv)
    glossary = load_glossary(a.glossary)
    for path in a.csv:
        rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
        changed = 0
        for r in rows:
            old = r.get("traducao", "")
            if not old:
                continue
            new = post_edit(old, glossary, space_fixes=False)
            if new != old:
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
        print("  %s: %d linhas ajustadas" % (dst, changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
