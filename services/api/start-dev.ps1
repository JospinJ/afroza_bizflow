# Demarrage rapide API (sans migrations ni seed)
Set-Location $PSScriptRoot
$py = "c:\Users\user\env_o\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=== Demarrage API (dev) ===" -ForegroundColor Cyan
& $py -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
