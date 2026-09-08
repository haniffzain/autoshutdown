# AutoShutdown

**AutoShutdown** is a compact desktop utility for scheduling power and application-control tasks on **Linux** and **Windows**.

It is developed as part of the **Hubuntu OS software ecosystem**: small, focused utilities designed to solve one job clearly, quickly and with minimal overhead.

## Features

- Timed **Shutdown**
- Timed **Restart**
- Timed **Logout**
- Timed **Close App**
- Timed **Restrict App**
- Live countdown display
- Quick presets: **5m, 15m, 30m, 1h, 2h, 3h**
- START / STOP controls
- Password-protected settings
- PBKDF2-SHA256 password hashing with random salt
- Animated Unicode / ASCII cat mascot
- Compact Tkinter desktop UI
- CLI mode with `--dry-run`

---

# Platform Builds

AutoShutdown uses one shared Python core while keeping separate install/build paths for Linux and Windows.

```text
AutoShutdown/
├── assets/
│   └── autoshutdown.svg
├── linux/
│   ├── install.sh
│   ├── run.sh
│   └── build-deb.sh
├── windows/
│   ├── install.ps1
│   ├── run.bat
│   └── build.ps1
├── .github/workflows/
│   └── build-release.yml
├── gui.py
├── autoshutdown.py
├── requirements.txt
└── README.md
```

### Linux

Primary Linux targets:

- Hubuntu / Ubuntu
- Debian-based distributions
- Arch Linux
- Fedora

### Windows

Primary Windows targets:

- Windows 10
- Windows 11

The application automatically selects the appropriate native power/logout commands for the detected operating system.

---

# Quick Install

## Ubuntu / Hubuntu

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-tk
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
./linux/run.sh
```

## Arch Linux

```bash
sudo pacman -S --needed git python tk
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
./linux/run.sh
```

## Fedora

```bash
sudo dnf install -y git python3 python3-tkinter
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
./linux/run.sh
```

## Windows 10 / 11

Install Python 3 and Git first, then run:

```powershell
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
.\windows\run.bat
```

---

# Packaged Builds

AutoShutdown includes release builders for Linux and Windows.

## Linux `.deb` package

On Hubuntu / Ubuntu / Debian:

```bash
cd autoshutdown
bash linux/build-deb.sh 0.2.1
```

Output:

```text
dist/autoshutdown_0.2.1_all.deb
```

Install or upgrade the package:

```bash
sudo apt install ./dist/autoshutdown_0.2.1_all.deb
```

Launch it from the desktop application menu or run:

```bash
autoshutdown
```

The Debian package installs:

```text
/opt/autoshutdown/gui.py
/opt/autoshutdown/autoshutdown.py
/usr/bin/autoshutdown
/usr/share/applications/autoshutdown.desktop
/usr/share/icons/hicolor/scalable/apps/autoshutdown.svg
```

The application menu entry includes:

- AutoShutdown application icon
- `Shutdown Scheduler` generic name
- desktop search keywords for shutdown, restart, logout, timer and app restriction
- Hubuntu-specific metadata
- desktop startup notification metadata

The Debian package declares these runtime dependencies:

- `python3 >= 3.10`
- `python3-tk`
- `python3-psutil`

### Test an installed Linux package

```bash
which autoshutdown
dpkg -L autoshutdown
dpkg -s autoshutdown | grep Version
autoshutdown
```

### Upgrade an existing package

Build a newer version and install it over the old package:

```bash
bash linux/build-deb.sh 0.2.1
sudo apt install ./dist/autoshutdown_0.2.1_all.deb
```

APT treats this as a normal package upgrade. The `0.2.0 -> 0.2.1` upgrade path has been tested successfully on Hubuntu.

### Remove the package

```bash
sudo apt remove autoshutdown
```

User password configuration under `~/.autoshutdown/` is intentionally not removed by the Debian package uninstall process.

---

## Standalone Windows `.exe`

From PowerShell on Windows:

```powershell
cd autoshutdown
powershell -ExecutionPolicy Bypass -File .\windows\build.ps1 -Version 0.2.1
```

Outputs:

```text
dist\AutoShutdown.exe
dist\AutoShutdown-0.2.1-Windows.exe
```

The Windows builder uses **PyInstaller** in one-file, windowed mode so the application can run without opening a console window.

The generated executable now includes Windows version-resource metadata:

- CompanyName: `Hubuntu OS Project`
- ProductName: `AutoShutdown`
- FileDescription: `AutoShutdown desktop utility`
- FileVersion / ProductVersion: supplied build version
- OriginalFilename: `AutoShutdown.exe`
- License metadata: MIT

The build script also validates that the executable exists and reports its final size before completing.

A dedicated Windows application icon and installer package remain planned release-polish items.

---

# Automatic GitHub Builds

The repository includes:

```text
.github/workflows/build-release.yml
```

GitHub Actions builds and validates two versioned artifacts:

```text
AutoShutdown-Linux-DEB-<version>
AutoShutdown-Windows-EXE-<version>
```

The workflow runs when:

- code is pushed to `main`
- a version tag such as `v0.2.1` is pushed
- the workflow is started manually

For normal `main` builds, artifacts receive development versions such as:

```text
0.2.1-dev.15
```

For a release tag:

```bash
git tag v0.2.1
git push origin v0.2.1
```

it produces release version:

```text
0.2.1
```

The Linux CI job verifies the generated Debian package with `dpkg-deb --info`. The Windows CI job verifies that the versioned executable was created before uploading it.

---

# First Launch & App Lock

On first launch, AutoShutdown asks you to create an administrator password.

The password protects task changes, timer changes, application selection, restrictions, cancellation and password changes.

The original password is not stored as plaintext.

Security configuration is stored under the user's home directory:

```text
~/.autoshutdown/security.json
```

It contains a random salt and PBKDF2-SHA256 password hash.

---

# Power Timer

Choose:

- `shutdown`
- `restart`
- `logout`

Then choose a preset or enter a duration such as:

```text
30s
5m
15m
30m
1h
2h
3h
```

Press **START** to activate the timer.

Example active display:

```text
ACTIVE   00:29:41   Shutdown
```

Press **STOP** to cancel a supported active task.

---

# Timed Close App

The **Close App** tab closes a selected process when the timer expires.

Examples:

```text
notepad.exe
firefox.exe
firefox
gnome-text-editor
```

Applications can contain unsaved work when they are closed.

---

# Timed Restrict App

The **Restrict** tab temporarily prevents a selected process from staying open.

You choose:

1. application / process
2. delay before restriction starts
3. restriction duration

During the restriction window, AutoShutdown checks for the matching process and closes it when detected.

This is a temporary runtime restriction. It does not permanently alter registry policy, permissions or operating-system security policy.

---

# Platform Behaviour

## Linux

AutoShutdown uses:

- shutdown / restart: `shutdown`
- logout: `loginctl`
- process control: `psutil`

Some Linux environments may require appropriate system permissions for power-management operations.

## Windows

AutoShutdown uses:

- shutdown: `shutdown /s`
- restart: `shutdown /r`
- logout: `shutdown /l`
- cancel scheduled shutdown/restart: `shutdown /a`
- process control: `psutil`

---

# CLI Mode

```bash
python autoshutdown.py shutdown --in 30m
python autoshutdown.py shutdown --at 23:30
python autoshutdown.py restart --in 10m
python autoshutdown.py logout --in 15m
python autoshutdown.py logout --at 22:00
python autoshutdown.py cancel
```

Safe command preview:

```bash
python autoshutdown.py shutdown --in 5m --dry-run
```

---

# Hubuntu OS Ecosystem

AutoShutdown is one of the small focused tools developed around the wider **Hubuntu OS software direction**.

```text
Hubuntu OS
   │
   ├── focused utilities
   │      ├── AutoShutdown
   │      ├── system tools
   │      ├── desktop utilities
   │      └── future Hubuntu applications
   │
   └── integrated desktop ecosystem
```

The idea is simple: each utility should remain small and understandable on its own while fitting naturally into the wider Hubuntu desktop environment.

AutoShutdown can also run independently on standard Linux distributions and Windows.

---

# Development Status

| Feature | Status |
|---|---|
| Linux source build | ✅ Available |
| Windows source build | ✅ Available |
| Timed shutdown / restart / logout | ✅ |
| Timed close app | ✅ |
| Timed restrict app | ✅ |
| Live countdown | ✅ |
| Password App Lock | ✅ |
| Compact GUI | ✅ |
| Animated cat mascot | ✅ |
| Debian `.deb` builder | ✅ Tested on Hubuntu |
| Linux package upgrade | ✅ 0.2.0 → 0.2.1 tested |
| Linux desktop launcher | ✅ |
| Linux application icon | ✅ |
| Standalone Windows `.exe` builder | ✅ |
| Windows executable metadata | ✅ |
| Versioned Windows release artifact | ✅ |
| GitHub Actions artifact validation | ✅ |
| Arch native package | Planned |
| Fedora RPM package | Planned |
| Windows application icon | Planned |
| Windows installer (`.msi` / setup `.exe`) | Planned |
| System tray | Planned |
| Multiple simultaneous tasks | Planned |
| Daily / weekly scheduler | Planned |
| Startup integration | Planned |
| Notification warnings | Planned |

---

# Release v0.2.1 direction

The `v0.2.1` milestone focuses on turning AutoShutdown into a reproducible, distributable desktop application for both Linux and Windows.

Current release work includes:

- tested Hubuntu / Ubuntu `.deb` package
- successful package upgrade from `0.2.0` to `0.2.1`
- Linux desktop launcher and application icon
- polished Linux package metadata
- Windows one-file executable builder
- Windows version-resource metadata
- versioned Windows release artifact
- automated GitHub artifact build validation
- release-oriented README documentation

Remaining polish before a broader release includes a dedicated Windows icon and a conventional Windows installer.

---

# Updating Source Installs

Linux:

```bash
cd ~/autoshutdown
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
./linux/run.sh
```

Windows:

```powershell
cd autoshutdown
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\windows\run.bat
```

---

# License

MIT License.
