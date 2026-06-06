# Exécute migrations SQL + seed (nécessite SUPABASE_DB_PASSWORD dans .env)
Set-Location $PSScriptRoot
$py = "c:\Users\user\env_o\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=== Migrations SQL Supabase ===" -ForegroundColor Cyan
& $py scripts/run_migrations.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Si SUPABASE_DB_PASSWORD manque:" -ForegroundColor Yellow
    Write-Host "  Supabase -> Settings -> Database -> Database password" -ForegroundColor Yellow
    Write-Host "  Ou collez 001 + 002 dans SQL Editor manuellement." -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Write-Host "=== Seed Salon Aicha ===" -ForegroundColor Cyan
& $py scripts/setup_db.py

Write-Host "=== Demarrage API ===" -ForegroundColor Cyan
& $py -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
