#!/usr/bin/env python3
"""
propósito: Pipeline etapa 1 - Analisar ISO/ROM
como usar: python3 core/pipeline/analyze.py <path-to-iso>
dependências: python3, 7z, file (opcionais)
como generalizar: Agnóstico
"""
import sys
import os
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime


ROOT = Path(__file__).parent.parent.parent


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze.py <iso-or-rom-path>")
        sys.exit(1)
    
    iso = Path(sys.argv[1])
    if not iso.exists():
        print(f"File not found: {iso}")
        sys.exit(1)
    
    reports = ROOT / "workspace/reports"
    reports.mkdir(parents=True, exist_ok=True)
    
    game_name = iso.name
    report = reports / f"{game_name}.analysis.md"
    
    print(f"Analyzing {iso}...")
    h = sha256_file(iso)
    print(f"SHA256: {h}")
    
    # file info
    try:
        r = subprocess.run(["file", str(iso)], stdout=subprocess.PIPE)
        ftype = r.stdout.decode()
    except:
        ftype = "unknown"
    
    content = f"""# Relatório de Análise (Etapa 1)

## Arquivo
{iso}

## SHA256
{h}

## Data
{datetime.now().isoformat()}

## Tipo (file)
```
{ftype}
```
"""
    report.write_text(content)
    print(f"Report: {report}")


if __name__ == '__main__':
    main()
