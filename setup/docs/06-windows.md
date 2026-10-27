# Configuração no Windows

## Recomendado: WSL2
O TraduzAI foi pensado para Linux. A melhor experiência no Windows é via WSL2.

```bash
wsl --install
# Após instalar Ubuntu, clone ou acesse o projeto dentro do WSL
cd /home/seu-usuario/TraduzAI-develop
bash setup/install.sh
bash setup/install/check.sh
```

## Alternativa: Nativo Windows
Se não puder usar WSL, use o modo nativo com Git Bash.

### Instalação
1. Instale [Git for Windows](https://git-scm.com/download/win) (inclui Git Bash)
2. Instale [Python](https://www.python.org/downloads/)
3. Instale [7-Zip](https://www.7-zip.org/)
4. Instale [ripgrep](https://github.com/BurntSushi/ripgrep) (`winget install BurntSushi.ripgrep.MSVC`)
5. (Opcional) [ImageMagick](https://imagemagick.org/script/download.php#windows)

### Verificação
Abra PowerShell na pasta do projeto:
```powershell
.\setup\install\windows\check.ps1
```

### Executando scripts
- Scripts Python: `py workspace\scripts\tbl_decode.py ...` ou `python ...`
- Scripts `.sh`: use Git Bash (`bash workspace/scripts/analyze_iso.sh`)
- PowerShell scripts: `.\caminho\script.ps1`

## Dicas
- Coloque ISOs/ROMs em `workspace/input/`
- Use `py` ao invés de `python3` no Windows
- `tree`, `file`, `binwalk` podem não existir nativamente - use WSL2 se precisar deles
- O agente (Claude Code, RooCode, Copilot) funciona normalmente no Windows
