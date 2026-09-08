# AutoShutdown

**AutoShutdown** is a compact desktop utility for scheduling power and application-control tasks on **Linux** and **Windows**.

It started as a small utility in the **Hubuntu OS ecosystem**: a collection of focused tools designed to solve one job clearly, quickly and with minimal overhead.

## What AutoShutdown can do

- Timed **Shutdown**
- Timed **Restart**
- Timed **Logout**
- Timed **Close App**
- Timed **Restrict App**
- Live countdown display
- Quick presets: **5m, 15m, 30m, 1h, 2h, 3h**
- START / STOP controls
- Password-protected settings
- PBKDF2-SHA256 password hashing with a random salt
- Animated Unicode / ASCII cat mascot
- Compact Tkinter desktop interface
- CLI mode with `--dry-run`

---

# Two platform builds

AutoShutdown keeps one shared Python engine while providing separate launch and installation paths for each platform.

```text
AutoShutdown/
├── linux/
│   ├── install.sh
│   └── run.sh
├── windows/
│   ├── install.ps1
│   └── run.bat
├── gui.py
├── autoshutdown.py
├── requirements.txt
└── README.md
```

### Linux build

Designed for Linux desktops including:

- Hubuntu / Ubuntu
- Arch Linux
- Fedora
- other modern Linux distributions using Python 3, Tk and systemd-compatible tools

### Windows build

Designed for:

- Windows 10
- Windows 11

The GUI is shared, while native shutdown, restart and logout commands are selected automatically for the detected operating system.

---

# Quick Install

## Ubuntu / Hubuntu

Install system requirements:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-tk
```

Clone AutoShutdown:

```bash
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
```

Install the Python environment:

```bash
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
```

Launch:

```bash
./linux/run.sh
```

You can also launch it manually:

```bash
source .venv/bin/activate
python gui.py
```

---

## Arch Linux

Install system requirements:

```bash
sudo pacman -S --needed git python tk
```

Clone and install:

```bash
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
```

Launch:

```bash
./linux/run.sh
```

---

## Fedora

Install system requirements:

```bash
sudo dnf install -y git python3 python3-tkinter
```

Clone and install:

```bash
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
chmod +x linux/install.sh linux/run.sh
./linux/install.sh
```

Launch:

```bash
./linux/run.sh
```

---

## Windows 10 / 11

### 1. Install Python

Install a current Python 3 release and make sure **Add Python to PATH** is enabled during installation.

Verify in PowerShell or Command Prompt:

```powershell
python --version
```

### 2. Install Git

Install Git for Windows and verify:

```powershell
git --version
```

### 3. Clone AutoShutdown

```powershell
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
```

### 4. Install the Windows environment

From PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
```

### 5. Launch AutoShutdown

```powershell
.\windows\run.bat
```

Or manually:

```powershell
.\.venv\Scripts\python.exe gui.py
```

---

# First launch

On first launch, AutoShutdown asks you to create an administrator password.

The password protects changes such as:

- starting a new task
- changing timers
- selecting applications
- starting app restrictions
- cancelling protected tasks
- changing the AutoShutdown password

The original password is **not stored as plaintext**.

Security data is stored under the user's home directory:

```text
~/.autoshutdown/security.json
```

The file contains a random salt and PBKDF2-SHA256 password hash.

---

# Power timer

Choose one of:

- `shutdown`
- `restart`
- `logout`

Then choose a preset or enter a custom duration such as:

```text
30s
5m
15m
30m
1h
2h
3h
```

Press **START** to activate the countdown.

The main header shows:

```text
ACTIVE   00:29:41   Shutdown
```

Press **STOP** to cancel an active supported task.

---

# Timed Close App

The **Close App** tab closes a selected process when its timer expires.

Example targets:

```text
notepad.exe
firefox.exe
firefox
gnome-text-editor
```

Process names differ between Linux and Windows.

> Applications may contain unsaved work when they are closed.

---

# Timed Restrict App

The **Restrict** tab temporarily prevents a selected application from remaining open.

You choose:

1. application / process
2. delay before restriction begins
3. restriction duration

While the restriction is active, AutoShutdown checks for the matching process and closes it when detected.

This is a temporary runtime restriction. It does **not** modify operating-system registry policies, file permissions or permanent security policies.

---

# Platform behaviour

## Linux

AutoShutdown uses Linux-native facilities where appropriate:

- shutdown / restart: `shutdown`
- logout: `loginctl`
- process control: `psutil`

Some Linux systems may require appropriate system permissions for power-management actions.

## Windows

AutoShutdown uses Windows-native facilities where appropriate:

- shutdown: `shutdown /s`
- restart: `shutdown /r`
- logout: `shutdown /l`
- cancel scheduled shutdown/restart: `shutdown /a`
- process control: `psutil`

---

# Command-line mode

The GUI is the primary interface, but AutoShutdown also includes a CLI.

Examples:

```bash
python autoshutdown.py shutdown --in 30m
python autoshutdown.py shutdown --at 23:30
python autoshutdown.py restart --in 10m
python autoshutdown.py logout --in 15m
python autoshutdown.py logout --at 22:00
python autoshutdown.py cancel
```

Test a command without executing the power action:

```bash
python autoshutdown.py shutdown --in 5m --dry-run
```

---

# Hubuntu OS ecosystem

AutoShutdown is developed as part of the wider **Hubuntu OS software direction**.

Hubuntu is built around the idea that an operating environment can grow through small, focused utilities instead of forcing every feature into one large application.

AutoShutdown demonstrates that approach:

```text
Hubuntu OS
   │
   ├── small focused utilities
   │      ├── AutoShutdown
   │      ├── system tools
   │      ├── desktop utilities
   │      └── future Hubuntu applications
   │
   └── one integrated desktop ecosystem
```

Each utility should remain understandable on its own while still fitting naturally into the Hubuntu desktop environment.

AutoShutdown can also run independently on standard Linux distributions and Windows.

---

# Requirements

Core requirements:

- Python 3.10+
- Tkinter / Tk
- `psutil`

Python dependency installation is handled by the included platform installers and `requirements.txt`.

---

# Development status

| Feature | Status |
|---|---|
| Linux build | ✅ Available |
| Windows build | ✅ Available |
| Timed shutdown | ✅ |
| Timed restart | ✅ |
| Timed logout | ✅ |
| Timed close app | ✅ |
| Timed restrict app | ✅ |
| Live countdown | ✅ |
| Password App Lock | ✅ |
| Compact GUI | ✅ |
| Animated cat mascot | ✅ |
| System tray | Planned |
| Multiple simultaneous tasks | Planned |
| Daily / weekly scheduler | Planned |
| Startup integration | Planned |
| Notification warnings | Planned |
| Packaged `.deb` / Arch package / RPM | Planned |
| Standalone Windows `.exe` | Planned |

---

# Updating

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
