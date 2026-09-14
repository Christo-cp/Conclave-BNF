# Full suite (plan A2). Run from anywhere with no API running; stops at the first failure.
# Refuses to start while port 8000 is listening: pytest and a running API would share
# smart_ambulance_test.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = Join-Path $root "apps\api\.venv\Scripts\python.exe"

if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) {
    throw "Port 8000 is listening. Stop the API before running the full suite."
}

function Invoke-Step([string]$Name, [scriptblock]$Command) {
    Write-Host "--- $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Step "pytest" { & $py -m pytest apps\api\tests -v }
Invoke-Step "ruff" { & $py -m ruff check apps\api }
Invoke-Step "web build" { pnpm --dir apps/web build }

$unitTests = Get-ChildItem apps\web\src -Recurse -File -Include *.test.ts, *.test.tsx -ErrorAction SilentlyContinue
if ($unitTests) {
    Invoke-Step "vitest" { pnpm --dir apps/web exec vitest run --reporter=verbose }
} else {
    Write-Host "--- vitest skipped: no web unit tests yet"
}

Write-Host "--- full suite passed"
