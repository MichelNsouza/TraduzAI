#!/usr/bin/env python3
"""
propósito: Verificar ambiente e ferramentas do TraduzAI
como usar: python3 core/doctor.py
dependências: python3, pyyaml (opcional)
como generalizar: Agnóstico
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

TOOLS = [
    "python3", "git", "7z", "tree", "file", "rg", "binwalk",
    "ffmpeg", "convert", "magick"
]


def check_cmd(cmd):
    try:
        r = subprocess.run(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return r.returncode == 0
    except:
        return False


def main():
    print("=" * 40)
    print(" TraduzAI Doctor")
    print("=" * 40)
    print()
    
    print("Core dirs:")
    for d in ["workspace/input", "workspace/extracted", "workspace/output", 
              "workspace/reports", "workspace/context", "workspace/scripts",
              "adapters", "core"]:
        p = ROOT / d
        print(f"  {'✓' if p.exists() else '✗'} {d}")
    print()
    
    print("Tools:")
    for t in TOOLS:
        ok = check_cmd(t)
        print(f"  {'✓' if ok else '✗'} {t}")
    print()
    
    print("Registry:")
    reg = ROOT / "core/registry/tools.yaml"
    print(f"  {'✓' if reg.exists() else '✗'} core/registry/tools.yaml")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
