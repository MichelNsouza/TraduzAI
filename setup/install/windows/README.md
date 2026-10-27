# Instalação no Windows

Existem duas formas de rodar o TraduzAI no Windows:
- **WSL2 (Recomendado)** - Mais fiel ao ambiente Linux usado pelo projeto
- **Nativo Windows (PowerShell)** - Funciona com ferramentas portáveis

## Opção 1: WSL2 (Recomendado)
1. Instale WSL2 com Ubuntu/Debian: `wsl --install`
2. Abra o terminal WSL na pasta do projeto (ou clone dentro do WSL)
3. Siga as instruções Linux: `bash setup/install.sh` ou use os scripts em `setup/install/`
4. Rode `bash setup/install/check.sh`

## Opção 2: Nativo Windows
1. Instale dependências via winget/chocolatey ou manualmente
2. Execute `setup\install\windows\install.ps1` no PowerShell (como usuário)
3. Execute `setup\install\windows\check.ps1` para validar
