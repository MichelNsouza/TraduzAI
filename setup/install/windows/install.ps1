#Requires -Version 5.1
<#
.SYNOPSIS
    Instalador TraduzAI para Windows (nativo)
.DESCRIPTION
    Verifica e orienta instalação de dependências via winget/chocolatey
.NOTES
    Recomendado usar WSL2. Este script é assistente/orientativo.
#>

Write-Host "==================================" -ForegroundColor Cyan
Write-Host " TraduzAI - Windows Setup (Nativo)" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

function Test-Command($cmd) {
    $null = Get-Command $cmd -ErrorAction SilentlyContinue
    return $?
}

Write-Host "Verificando gerenciadores..." -ForegroundColor Yellow
$hasWinget = Test-Command "winget"
$hasChoco  = Test-Command "choco"
$hasScoop  = Test-Command "scoop"

Write-Host "  winget: $(if($hasWinget){'OK'}else{'N/A'})"
Write-Host "  choco:  $(if($hasChoco){'OK'}else{'N/A'})"
Write-Host "  scoop:  $(if($hasScoop){'OK'}else{'N/A'})"
Write-Host ""

Write-Host "Pacotes sugeridos:" -ForegroundColor Yellow
Write-Host "  - Python 3.11+ (python.org ou Microsoft Store)"
Write-Host "  - Git for Windows"
Write-Host "  - 7-Zip"
Write-Host "  - ripgrep (rg)"
Write-Host "  - ImageMagick"
Write-Host "  - GnuWin32 tools (opcional) ou use Git Bash"
Write-Host ""

if ($hasWinget) {
    Write-Host "Comandos winget sugeridos:" -ForegroundColor Cyan
    Write-Host "  winget install Python.Python.3.11"
    Write-Host "  winget install Git.Git"
    Write-Host "  winget install 7zip.7zip"
    Write-Host "  winget install BurntSushi.ripgrep.MSVC"
    Write-Host "  winget install ImageMagick.ImageMagick"
    Write-Host ""
}

Write-Host "Dicas:" -ForegroundColor Yellow
Write-Host "  - Prefira Git Bash para rodar scripts .sh do projeto"
Write-Host "  - Para melhor compatibilidade, use WSL2 (ver README.md acima)"
Write-Host "  - Python scripts rodam nativamente com 'python' ou 'py'"
Write-Host ""
Write-Host "Após instalar, rode: .\setup\install\windows\check.ps1" -ForegroundColor Green
