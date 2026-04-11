# Script PowerShell para instalar dependências
# Execute no PowerShell como administrador

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Instalando dependencias - FG Auto Pecas" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ativar o ambiente virtual
Write-Host "Ativando ambiente virtual Python..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Instalando dependencias..." -ForegroundColor Yellow
Write-Host ""

$packages = @("Flask", "werkzeug", "psycopg2-binary", "python-dotenv", "pytz")

foreach ($package in $packages) {
    Write-Host "  >> Instalando $package..." -ForegroundColor Cyan
    python -m pip install $package --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "     OK $package" -ForegroundColor Green
    } else {
        Write-Host "     ERRO ao instalar $package" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Instalacao concluida!" -ForegroundColor Cyan
Write-Host "  Para testar a conexao, execute: python test_diagnostic.py" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
