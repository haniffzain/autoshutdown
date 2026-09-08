param(
    [string]$Version = "0.2.1"
)

$ErrorActionPreference = 'Stop'
$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python 3 is required and must be available in PATH.'
}

if ($Version -notmatch '^\d+\.\d+\.\d+([-.][A-Za-z0-9.]+)?$') {
    throw "Invalid version format: $Version"
}

if (-not (Test-Path '.build-venv')) {
    python -m venv .build-venv
}

$Python = '.\.build-venv\Scripts\python.exe'
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install 'pyinstaller>=6,<7'

$NumericVersion = ($Version -split '[-+]')[0]
$Parts = $NumericVersion.Split('.')
$Major = [int]$Parts[0]
$Minor = [int]$Parts[1]
$Patch = [int]$Parts[2]
$VersionTuple = "$Major, $Minor, $Patch, 0"

$VersionFile = Join-Path $RootDir 'windows\version-info.txt'
@"
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($VersionTuple),
    prodvers=($VersionTuple),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'Hubuntu OS Project'),
          StringStruct('FileDescription', 'AutoShutdown desktop utility'),
          StringStruct('FileVersion', '$Version'),
          StringStruct('InternalName', 'AutoShutdown'),
          StringStruct('LegalCopyright', 'MIT License'),
          StringStruct('OriginalFilename', 'AutoShutdown.exe'),
          StringStruct('ProductName', 'AutoShutdown'),
          StringStruct('ProductVersion', '$Version')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@ | Set-Content -Encoding UTF8 $VersionFile

if (Test-Path 'build') { Remove-Item -Recurse -Force 'build' }
if (Test-Path 'dist\AutoShutdown.exe') { Remove-Item -Force 'dist\AutoShutdown.exe' }

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name AutoShutdown `
    --version-file $VersionFile `
    gui.py

$BuiltExe = Join-Path $RootDir 'dist\AutoShutdown.exe'
if (-not (Test-Path $BuiltExe)) {
    throw 'Build failed: dist\AutoShutdown.exe was not created.'
}

$VersionedExe = Join-Path $RootDir "dist\AutoShutdown-$Version-Windows.exe"
Copy-Item -Force $BuiltExe $VersionedExe

$SizeMB = [math]::Round((Get-Item $BuiltExe).Length / 1MB, 2)
Write-Host "Built: dist\AutoShutdown.exe ($SizeMB MB)"
Write-Host "Release artifact: dist\AutoShutdown-$Version-Windows.exe"
