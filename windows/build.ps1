$ErrorActionPreference = 'Stop'
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3 is required and must be available in PATH.'
}

if (-not (Test-Path '.build-venv')) {
    python -m venv .build-venv
}

$Python = '.\.build-venv\Scripts\python.exe'
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install 'pyinstaller>=6,<7'

if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }
if (Test-Path 'dist\AutoShutdown.exe') { Remove-Item -Force 'dist\AutoShutdown.exe' }

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name AutoShutdown `
    gui.py

Write-Host 'Built: dist\AutoShutdown.exe'
