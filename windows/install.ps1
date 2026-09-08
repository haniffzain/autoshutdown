$ErrorActionPreference = 'Stop'
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3 is required and must be available in PATH.'
}

if (-not (Test-Path '.venv')) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host 'AutoShutdown Windows dependencies installed.'
Write-Host 'Run with: windows\run.bat'
