# AutoShutdown

**AutoShutdown** is a compact desktop utility for scheduling power and application-control tasks on **Linux** and **Windows**.

It is developed as part of the **Hubuntu OS software ecosystem**: small, focused utilities designed to solve one job clearly with minimal overhead.

## Current features

- Timed **Shutdown / Restart / Logout**
- Timed **Close App** and temporary **Restrict App**
- Multiple-task engine
- Daily / weekly scheduler core
- Persistent task history
- User-level startup integration
- Live countdown and quick presets
- Password-protected settings using PBKDF2-SHA256
- System tray and Hide to Tray
- Desktop notifications
- Automatic desktop light/dark tone matching
- Animated Unicode cat mascot
- Full MIT License inside the app
- GitHub release update checker
- Git source auto-update with safe `git pull --ff-only`
- Linux `.deb`, Windows `.exe`, and Snap packaging paths

---

# Project layout

```text
AutoShutdown/
├── assets/
│   └── autoshutdown.svg
├── core/
│   ├── history_store.py
│   ├── scheduler_store.py
│   ├── startup.py
│   ├── task_manager.py
│   └── update_checker.py
├── linux/
│   ├── install.sh
│   ├── run.sh
│   └── build-deb.sh
├── snap/
│   └── snapcraft.yaml
├── windows/
│   ├── install.ps1
│   ├── run.bat
│   └── build.ps1
├── advanced_controller.py
├── desktop_integration.py
├── desktop_theme.py
├── gui.py
├── autoshutdown.py
├── update.py
├── version.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

# Quick source install

## Hubuntu / Ubuntu

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-tk
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python gui.py
```

## Arch Linux

```bash
sudo pacman -S --needed git python tk
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python gui.py
```

## Fedora

```bash
sudo dnf install -y git python3 python3-tkinter
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python gui.py
```

## Windows 10 / 11

```powershell
git clone https://github.com/haniffzain/autoshutdown.git
cd autoshutdown
powershell -ExecutionPolicy Bypass -File .\windows\install.ps1
.\windows\run.bat
```

---

# Auto-update architecture

AutoShutdown does **not** blindly replace itself from the `main` branch for every installation type. Each package uses the update channel appropriate for that installation.

## Git source install

The updater can safely update a clean Git checkout using fast-forward only:

```bash
python update.py --apply
```

Internally this uses:

```text
git status --porcelain
git pull --ff-only
```

If local files have uncommitted changes, the updater stops instead of overwriting them.

Check the latest published GitHub release without applying anything:

```bash
python update.py --check
```

## Snap install

Snap installations are updated by **snapd** through the Snap Store refresh mechanism. AutoShutdown detects the Snap environment and does not attempt to overwrite files inside the snap.

Manual refresh when needed:

```bash
sudo snap refresh autoshutdown
```

## Debian `.deb`

The installed package contains the update checker:

```bash
autoshutdown-update --check
```

A `.deb` installation should ultimately update through an APT repository or a verified GitHub Release package. It does not silently replace `/opt/autoshutdown` from `main`.

## Windows `.exe`

Windows builds check GitHub Releases. Automatic installer replacement is kept separate from the source updater so a future signed Windows installer can perform controlled upgrades.

The update service is implemented in:

```text
core/update_checker.py
update.py
```

The published-version source is:

```text
https://github.com/haniffzain/autoshutdown/releases/latest
```

---

# Linux `.deb` package

Build:

```bash
bash linux/build-deb.sh 0.4.0
```

Output:

```text
dist/autoshutdown_0.4.0_all.deb
```

Install / upgrade:

```bash
sudo apt install ./dist/autoshutdown_0.4.0_all.deb
```

Useful commands:

```bash
autoshutdown
autoshutdown-update --check
dpkg -s autoshutdown | grep Version
```

The package installs the application under `/opt/autoshutdown`, exposes `/usr/bin/autoshutdown`, and installs its desktop launcher/icon.

---

# Windows standalone build

From Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\build.ps1 -Version 0.4.0
```

Expected outputs:

```text
dist\AutoShutdown.exe
dist\AutoShutdown-0.4.0-Windows.exe
```

The Windows executable includes product/version metadata. A dedicated Windows icon and conventional installer remain part of the release-polish work.

---

# Snap package / Ubuntu App Center

The repository now contains:

```text
snap/snapcraft.yaml
```

Build the snap from the repository root:

```bash
sudo snap install snapcraft --classic
snapcraft
```

AutoShutdown currently requests **classic confinement** because its purpose requires broad interaction with system power commands and other running processes. Publishing a classic snap may require Snap Store review/approval.

After the Snap name is registered and the package is accepted in the Snap Store, the same Snap listing can be discoverable through Ubuntu's graphical software/App Center experience where Snap Store content is enabled.

Typical publishing flow after Store setup:

```bash
snapcraft login
snapcraft register autoshutdown
snapcraft upload --release=edge autoshutdown_*.snap
```

Promote to stable only after testing:

```bash
snapcraft release autoshutdown <revision> stable
```

Store publication requires the project owner's Snapcraft/Ubuntu account and any required classic-confinement review; repository code alone cannot complete that account-side approval.

---

# Desktop theme matching

AutoShutdown follows the desktop's light/dark preference.

- Hubuntu / Ubuntu / GNOME: `gsettings` colour preference, with GTK theme fallback
- Windows: application theme preference from the current user's Windows theme settings

The palette is applied to the main window, mascot panel, controls, tabs, password dialogs, and MIT License viewer.

---

# App Lock

On first launch AutoShutdown asks for an administrator password. The original password is not stored in plaintext.

Configuration is stored in:

```text
~/.autoshutdown/security.json
```

The app uses PBKDF2-HMAC-SHA256 with a random salt.

This is application-level protection; it is not a substitute for operating-system account security or filesystem permissions.

---

# Scheduler, tasks and history

Core modules already exist for:

- multiple simultaneous in-process tasks
- daily schedules
- weekly schedules and weekday selection
- persistent schedules
- enable/disable schedule entries
- persistent task history
- user-level startup integration

The GUI integration layer is implemented through `advanced_controller.py` and is being connected into the compact themed interface.

Persistent data lives under:

```text
~/.autoshutdown/
```

---

# GitHub Actions

The repository includes automated Linux and Windows build jobs in:

```text
.github/workflows/build-release.yml
```

Release tags follow the normal form:

```bash
git tag v0.4.0
git push origin v0.4.0
```

GitHub Releases are also the canonical update-check source used by AutoShutdown.

---

# Development status

| Feature | Status |
|---|---|
| Linux source build | ✅ |
| Windows source build | ✅ |
| Shutdown / restart / logout | ✅ |
| Close / Restrict App | ✅ |
| Password App Lock | ✅ |
| Desktop theme matching | ✅ |
| System tray / notifications | ✅ |
| In-app MIT License | ✅ |
| Debian `.deb` builder | ✅ Tested on Hubuntu |
| Windows `.exe` builder | ✅ |
| Multiple-task core | ✅ |
| Daily / weekly scheduler core | ✅ |
| Startup integration core | ✅ |
| Persistent history core | ✅ |
| GitHub Release update checker | ✅ |
| Git source auto-update | ✅ |
| Snap packaging definition | ✅ Initial build |
| Advanced GUI integration | In progress |
| Snap Store publication | Account/review step required |
| Windows application icon | Planned |
| Windows installer | Planned |
| Signed package auto-upgrade | Planned |

---

# License

AutoShutdown is released under the **MIT License**.

The complete license text is available in:

- `LICENSE`
- **About → View License** inside AutoShutdown
