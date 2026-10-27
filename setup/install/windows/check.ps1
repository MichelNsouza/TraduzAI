#Requires -Version 5.1
<#
.SYNOPSIS
    Verificador TraduzAI para Windows
#>

Write-Host "==================================" -ForegroundColor Cyan
Write-Host " TraduzAI - Windows Environment Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

function Test-Command($cmd) {
    $null = Get-Command $cmd -ErrorAction SilentlyContinue
    return $?
}

function Check($cmd) {
    if (Test-Command $cmd) {
        Write-Host "✓ $cmd" -ForegroundColor Green
    } else {
        Write-Host "✗ $cmd AUSENTE" -ForegroundColor Red
    }
}

Write-Host "Ferramentas:" -ForegroundColor Yellow
Check "python"
Check "py"
Check "pip"
Check "git"
Check "7z"
Check "rg"
Check "ffmpeg"
Check "magick"
Check "convert"

Write-Host ""
Write-Host "Versões:" -ForegroundColor Yellow
if (Test-Command "py") { py --version }
if (Test-Command "python") { python --version 2>$null }
if (Test-Command "git") { git --version }

Write-Host ""
Write-Host "Nota: 'tree', 'file', 'binwalk' são mais comuns no Linux/WSL." -ForegroundColor Gray
Write-Host "Para máxima compatibilidade, considere usar WSL2." -ForegroundColor Gray
Write-Host ""
Write-Host "Verificação concluída." -ForegroundColor Cyan
