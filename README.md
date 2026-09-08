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
- **Automatic desktop light/dark theme matching**
- **System tray integration**
- **Hide to Tray** behaviour
- Tray menu: **Open / Hide / Stop Task / Exit**
- Desktop notifications when a task starts and when one minute remains
- Full **MIT License** available inside the About tab
- CLI mode with `--dry-run`

---

# Platform Builds

AutoShutdown uses one shared Python core while keeping separate install/build paths for Linux and Windows.

```text
AutoShutdown/
├── assets/
│   └── autoshutdown.svg
├── core/
│   ├── history_store.py
│   ├── scheduler_store.py
│   ├── startup.py
│   └── task_manager.py
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
├── desktop_integration.py
├── desktop_theme.py
├── gui.py
├── autoshutdown.py
├── requirements.txt
├── LICENSE
└── README.md
```

### Linux targets

- Hubuntu / Ubuntu
- Debian-based distributions
- Arch Linux
- Fedora

### Windows targets

- Windows 10
- Windows 11

The application automatically selects the appropriate native power/logout commands for the detected operating system.

---

# Desktop Theme Matching

AutoShutdown now follows the desktop's light/dark preference instead of forcing its own fixed colour scheme.

On **Hubuntu / Ubuntu / GNOME**, AutoShutdown checks the GNOME desktop colour preference through `gsettings` and uses the current GTK theme as a fallback.

On **Windows**, it reads the current application light/dark preference from the user's Windows theme settings.

The detected theme is applied to:

- application background
- side mascot panel
- labels and status text
- buttons
- entries and comboboxes
- notebook tabs
- password dialogs
- MIT License viewer

The theme is detected when AutoShutdown starts. Restart AutoShutdown after changing the desktop theme to apply the new tone.

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

# Desktop Integration Phase

AutoShutdown includes a cross-platform tray layer in:

```text
desktop_integration.py
```

The tray menu provides:

```text
Open AutoShutdown
Hide Window
Stop Task
Exit
```

Pressing the window close button hides AutoShutdown to the tray when tray support is available. Use **Exit** from the tray menu to fully close the application.

The tray title follows the active task and countdown, for example:

```text
AutoShutdown - Shutdown - 00:14:52
```

AutoShutdown sends a desktop notification when a task is scheduled and another warning when the timer reaches approximately one minute remaining.

Tray controls do not bypass App Lock. Stopping a protected task from the tray returns to the main window and still requires the normal password unlock flow.

Tray support uses:

- `pystray`
- `Pillow`

If tray support is unavailable, the **Tray** button falls back to normal window minimization.

---

# Packaged Builds

## Linux `.deb` package

On Hubuntu / Ubuntu / Debian:

```bash
cd autoshutdown
bash linux/build-deb.sh 0.3.0
```

Output:

```text
dist/autoshutdown_0.3.0_all.deb
```

Install or upgrade:

```bash
sudo apt install ./dist/autoshutdown_0.3.0_all.deb
```

Launch from the desktop menu or run:

```bash
autoshutdown
```

The Debian package installs:

```text
/opt/autoshutdown/gui.py
/opt/autoshutdown/autoshutdown.py
/opt/autoshutdown/desktop_integration.py
/opt/autoshutdown/desktop_theme.py
/usr/bin/autoshutdown
/usr/share/applications/autoshutdown.desktop
/usr/share/icons/hicolor/scalable/apps/autoshutdown.svg
```

Runtime dependencies include:

- `python3 >= 3.10`
- `python3-tk`
- `python3-psutil`
- `python3-pil`
- `python3-pystray`

Test an installed package:

```bash
which autoshutdown
dpkg -L autoshutdown
dpkg -s autoshutdown | grep Version
autoshutdown
```

Remove the package:

```bash
sudo apt remove autoshutdown
```

User configuration under `~/.autoshutdown/` is intentionally retained during package removal.

---

## Standalone Windows `.exe`

From PowerShell on Windows:

```powershell
cd autoshutdown
powershell -ExecutionPolicy Bypass -File .\windows\build.ps1 -Version 0.3.0
```

Outputs:

```text
dist\AutoShutdown.exe
dist\AutoShutdown-0.3.0-Windows.exe
```

The Windows builder uses **PyInstaller** in one-file, windowed mode and includes imported tray/theme dependencies automatically.

Windows executable metadata includes:

- CompanyName: `Hubuntu OS Project`
- ProductName: `AutoShutdown`
- FileDescription: `AutoShutdown desktop utility`
- FileVersion / ProductVersion: supplied build version
- OriginalFilename: `AutoShutdown.exe`
- License metadata: MIT

---

# Automatic GitHub Builds

The repository includes:

```text
.github/workflows/build-release.yml
```

GitHub Actions builds and validates versioned artifacts for Linux and Windows.

A release tag such as:

```bash
git tag v0.3.0
git push origin v0.3.0
```

produces versioned build artifacts through the workflow.

---

# First Launch & App Lock

On first launch, AutoShutdown asks you to create an administrator password.

The password protects task changes, timer changes, application selection, restrictions, cancellation and password changes.

The original password is not stored as plaintext. Security configuration is stored at:

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

Press **START** to activate the timer. Press **STOP** to cancel a supported active task.

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
- tray integration: `pystray`
- desktop theme preference: GNOME `gsettings`

Some Linux environments may require appropriate system permissions for power-management operations.

## Windows

AutoShutdown uses:

- shutdown: `shutdown /s`
- restart: `shutdown /r`
- logout: `shutdown /l`
- cancel scheduled shutdown/restart: `shutdown /a`
- process control: `psutil`
- tray integration: `pystray`
- desktop theme preference: Windows user theme settings

---

# CLI Mode

```bash
python autoshutdown.py shutdown --in 30m
python autoshutdown.py shutdown --at 23:30
python autoshutdown.py restart --in 10m
python autoshutdown.py logout --in 15m
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

Each utility should remain small and understandable on its own while fitting naturally into the wider Hubuntu desktop environment.

---

# Development Status

| Feature | Status |
|---|---|
| Linux source build | ✅ |
| Windows source build | ✅ |
| Timed shutdown / restart / logout | ✅ |
| Timed close app | ✅ |
| Timed restrict app | ✅ |
| Live countdown | ✅ |
| Password App Lock | ✅ |
| Compact GUI | ✅ |
| Desktop light/dark tone matching | ✅ |
| In-app MIT License viewer | ✅ |
| Animated cat mascot | ✅ |
| Debian `.deb` builder | ✅ Tested on Hubuntu |
| Linux package upgrade | ✅ 0.2.0 → 0.2.1 tested |
| Linux desktop launcher/icon | ✅ |
| Standalone Windows `.exe` builder | ✅ |
| Windows executable metadata | ✅ |
| GitHub Actions artifact validation | ✅ |
| System tray | ✅ Initial cross-platform build |
| Hide to Tray | ✅ |
| Tray task status | ✅ |
| Desktop timer warnings | ✅ Initial build |
| Windows application icon | Planned |
| Windows installer | Planned |
| Multiple simultaneous tasks | Core added; UI integration pending |
| Daily / weekly scheduler | Core added; UI integration pending |
| Startup integration | Core added; UI integration pending |
| Persistent task history | Core added; UI integration pending |

---

# Current Development Direction

The core modules for the next major phase have already been added:

- `core/task_manager.py`
- `core/scheduler_store.py`
- `core/startup.py`
- `core/history_store.py`

The next GUI integration phase will expose these through dedicated **Tasks**, **Schedule**, **History** and **Settings** tabs.

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

AutoShutdown is released under the **MIT License**.

The complete license text is available in:

- the repository `LICENSE` file
- the application's **About → View License** window
