<p align="center">
  <img src="assets/logo.svg" alt="TouchFlow Logo" width="128" height="128">
</p>

<h1 align="center">TouchFlow Keyboard</h1>

<p align="center">
  <strong>On-screen keyboard for touch-enabled Linux</strong><br>
  Multitouch · RU/EN/UK/DE/FR · Learning · Overlay · KDE Wayland
</p>

<p align="center">
  <a href="https://github.com/eturnercus/keyboard/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version 1.0.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-green" alt="License GPL-3.0"></a>
  <a href="https://github.com/eturnercus/keyboard"><img src="https://img.shields.io/badge/platform-Linux-lightgrey" alt="Platform Linux"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/lang-Русский-blue" alt="Russian README"></a>
</p>

<p align="center">
  <a href="https://github.com/eturnercus/keyboard">Repository</a> ·
  <a href="https://github.com/eturnercus/keyboard/releases/tag/v1.0.0">Releases</a> ·
  <a href="README.md">Русский README</a>
</p>

---

## Features

**TouchFlow** is an on-screen keyboard for tablets, kiosks, panels, and 2-in-1 devices on Linux (Debian, Ubuntu, Fedora, Arch, and others).

### Keyboard and input

- **Multitouch** — up to 10 simultaneous touches
- **Auto-show** on text field focus via AT-SPI
- **Learning engine** — remembers where you hide the keyboard; show threshold and per-app rules (`auto`, `always_show`, `always_hide`)
- **Overlay / gamepad** — semi-transparent joystick and buttons (phone-style)
- **Languages:** Russian, English, Ukrainian, German, French (RU/EN/UK/DE/FR)
- **Quick actions:** copy, paste, cut, select all, undo, redo, find (Ctrl+C/V/X/A/Z/Y/F)
- **F-keys** (F1–F12), **numpad**, **arrow row**
- **Hide on external keyboard** (USB/BT)
- **Swipe from bottom** to show the keyboard

### System integration

- **KDE Wayland** — virtual keyboard (`X-KDE-Wayland-VirtualKeyboard`)
- **GNOME a11y** — on-screen keyboard via `gsettings`
- **Physical bindings** for hardware buttons via evdev
- **D-Bus** API (`com.touchflow.Keyboard`) and **CLI** (`touchflow-cli`)

### Installation and maintenance

- **First-run onboarding** — 6-step walkthrough (shown once)
- **Per-app learning rules** in settings and `config.toml`
- **Python 1.0.0** — production build with full settings GUI
- **C++ 1.0.0** — experimental native build (GTK4, no Python at runtime)
- **`touchflow-doctor`** — installation diagnostics (PATH, binaries, systemd, uinput, KDE desktop)
- **AppImage installers:** Install Python, Install C++, Uninstall

---

## Quick Start

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-1.0.0.sh -o install-touchflow.sh
chmod +x install-touchflow.sh
./install-touchflow.sh
```

Log out and back in for the `input` group, then open **Settings** → `touchflow-settings` or select TouchFlow in KDE.

---

## Installation

> **Download builds:** https://github.com/eturnercus/keyboard/releases/tag/v1.0.0

### Python AppImage (recommended)

```bash
# x86_64
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Keyboard-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Keyboard-1.0.0-x86_64.AppImage
./TouchFlow-Keyboard-1.0.0-x86_64.AppImage
```

For **aarch64**, use `TouchFlow-Keyboard-1.0.0-aarch64.AppImage`. A graphical installer opens — click **Install**.

### Python shell installer (curl)

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-1.0.0.sh | bash
```

Works on any architecture; installs dependencies, pip package, systemd, and desktop files.

### From git (`./scripts/install.sh`)

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
./scripts/install.sh
```

### C++ AppImage (experimental)

```bash
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
./TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
```

### C++ shell installer (`install-cpp`)

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-cpp-1.0.0.sh | bash
```

Or from source: `./scripts/install-cpp.sh`

### Requirements

| Component | Purpose |
|-----------|---------|
| **`input` group** | Access to `/dev/uinput` for key injection |
| **Wayland** (KDE) | KDE virtual keyboard list — Wayland only, not X11 |
| GTK4, AT-SPI | UI and auto-show on focus |
| `python3-evdev` | External keyboard detection (Python) |

**Debian/Ubuntu (Python):**

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-atspi-2.0 python3-evdev at-spi2-core
```

**Debian/Ubuntu (C++):**

```bash
sudo apt install build-essential cmake pkg-config g++ \
  libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev at-spi2-core
```

---

## After install

```bash
touchflow-doctor                              # diagnostics
touchflow-settings                            # settings (full path: ~/.local/bin/touchflow-settings)
systemctl --user status touchflow-daemon      # Python daemon status
systemctl --user restart touchflow-daemon     # restart
journalctl --user -u touchflow-daemon -e      # logs
```

For C++: `systemctl --user status touchflow-daemon-cpp`

If `touchflow-settings` is not found — check `echo $PATH` (needs `~/.local/bin`) or run `touchflow-doctor`.

**Log out and back in** after install (`sudo usermod -aG input $USER`).

---

## Settings

| Command | Version | Description |
|---------|---------|-------------|
| `touchflow-settings` | Python (production) | Full GUI: 10 sections (Libadwaita) |
| `touchflow-settings-cpp` | C++ (experimental) | Simplified C++ settings |

**`touchflow-settings` sections:**

| Section | Contents |
|---------|----------|
| Behavior | Auto-show, swipe, multitouch, external keyboard |
| Languages | RU, EN, UK, DE, FR; default language |
| Learning | Threshold, per-app rules, history, reset |
| Layout | Height, F-row, numpad, quick actions |
| Fonts | Family, size |
| Colors | 6 theme colors |
| Overlay | Joystick, opacity, positions |
| Buttons | Physical evdev bindings |
| Login screen | Greeter (pre-login) |
| About | Reset, replay onboarding |

Python config: `~/.config/touchflow/config.toml` — example in [docs/config.example.toml](docs/config.example.toml).

C++ config: `~/.config/touchflow/config-cpp.toml`

---

## KDE Virtual Keyboard (Wayland only)

1. Confirm a **Wayland** session (not X11): `echo $XDG_SESSION_TYPE`
2. Install TouchFlow (`./scripts/install.sh` or Python AppImage)
3. **Log out and back in** (`input` group)
4. Open **System Settings** → **Input Devices** → **Virtual Keyboard**
5. Select **TouchFlow** (or **TouchFlow C++** for the C++ build)
6. If TouchFlow is missing from the list:
   ```bash
   touchflow-doctor
   kbuildsycoca6 --noincremental   # or kbuildsycoca5
   ```
7. Restart the KDE session

> Do not run Python and C++ daemons at the same time. In KDE, pick **one** virtual keyboard.

---

## Uninstall

### `uninstall.sh` script

```bash
./scripts/uninstall.sh                        # with confirmation
./scripts/uninstall.sh -y                       # no prompts
./scripts/uninstall.sh -y --purge-config        # + ~/.config/touchflow
```

### Uninstall AppImage

```bash
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Uninstall-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Uninstall-1.0.0-x86_64.AppImage
./TouchFlow-Uninstall-1.0.0-x86_64.AppImage
```

Removes Python and C++ components (daemons, systemd, desktop files, pip).

### `make uninstall`

```bash
make uninstall   # runs scripts/uninstall.sh -y
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **`touchflow-settings` not found** | `echo $PATH` — add `~/.local/bin`; log out/in; run `touchflow-doctor` |
| **`touchflow-doctor` reports errors** | Reinstall: `./scripts/install.sh`; check `~/.local/bin/touchflow-settings` |
| **`TypeError: pressed` in journalctl** | Upgrade to **1.0.0** — GTK4 signal fixed (`clicked` instead of `pressed`) |
| **`uinput init failed` / keys not typed** | `sudo usermod -aG input $USER` and **log out/in** |
| **TouchFlow not in KDE virtual keyboard list** | **Wayland** only; `./scripts/install.sh`; **Settings → Input Devices → Virtual Keyboard → TouchFlow**; `kbuildsycoca6 --noincremental` |
| **AppImage does nothing** | `sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 zenity` |
| **Daemon not running** | `systemctl --user status touchflow-daemon` and `journalctl --user -u touchflow-daemon -e` |
| **Does not appear on focus** | `at-spi2-core`; `export GTK_MODULES=gail:atk-bridge` |
| **Does not hide on USB keyboard** | Settings → Behavior → “Hide on external keyboard” |
| **Learning gets in the way** | Settings → Learning → `always_show` rule or reset |

---

## C++ 1.0.0 (experimental)

Native daemon **`touchflowd-cpp`** — C++20 + GTK4 + libadwaita. Status: **experimental**; use Python for production.

| | Python 1.0.0 | C++ 1.0.0 |
|---|--------------|-----------|
| Status | **Production** | **Experimental** |
| Daemon | `touchflowd` | `touchflowd-cpp` |
| Settings | `touchflow-settings` (GUI) | `touchflow-settings-cpp` |
| systemd | `touchflow-daemon.service` | `touchflow-daemon-cpp.service` |
| Languages | RU/EN/UK/DE/FR | RU/EN |
| Learning | Full + per-app | Basic (threshold) |
| Overlay / gamepad | Yes | No |
| Install | AppImage / `install.sh` / curl | C++ AppImage / `install-cpp.sh` |
| Config | `config.toml` | `config-cpp.toml` |

Details: [`experimental/touchflow-cpp/README.md`](experimental/touchflow-cpp/README.md)

```bash
touchflowd-cpp                    # normal mode
touchflowd-cpp --virtual-keyboard # KDE/GNOME virtual keyboard mode
```

---

## CLI and D-Bus

**D-Bus:** `com.touchflow.Keyboard` at `/com/touchflow/Keyboard`

| Command | Action |
|---------|--------|
| `touchflow-cli show` | Show keyboard |
| `touchflow-cli hide` | Hide keyboard |
| `touchflow-cli toggle` | Show/hide |
| `touchflow-cli overlay` | Toggle overlay (gamepad) |
| `touchflow-cli reload` | Reload config |
| `touchflow-cli reset-learning` | Reset learning data |

The daemon must be running (`systemctl --user status touchflow-daemon`).

---

## Development

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
pip install -e ".[dev]"

make test           # pytest (tests/)
make lint           # ruff
make appimage       # dist/TouchFlow-Keyboard-1.0.0-x86_64.AppImage
make appimage-cpp   # dist/TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
make appimage-all   # Python + C++ + Uninstall AppImages
make release        # wheel + tar.gz in dist/
```

---

## License

[GPL-3.0-or-later](LICENSE) — TouchFlow Keyboard © TouchFlow Contributors
