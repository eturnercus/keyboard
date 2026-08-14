"""Интеграция с системными настройками (KDE, GNOME, systemd)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

DESKTOP_FILES = (
    "com.touchflow.Settings.desktop",
    "com.touchflow.Keyboard.desktop",
    "com.touchflow.Keyboard.Virtual.desktop",
)


def _home() -> Path:
    return Path.home()


def touchflowd_path() -> str:
    found = shutil.which("touchflowd")
    if found:
        return found
    local = _home() / ".local" / "bin" / "touchflowd"
    if local.exists():
        return str(local)
    return "touchflowd"


def install_desktop_files(project_root: Path) -> Path:
    apps = _home() / ".local" / "share" / "applications"
    icons = _home() / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps"
    apps.mkdir(parents=True, exist_ok=True)
    icons.mkdir(parents=True, exist_ok=True)

    bin_path = touchflowd_path()
    for name in DESKTOP_FILES:
        src = project_root / "data" / name
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8")
        # Подставляем реальный путь к touchflowd
        text = text.replace("Exec=touchflowd", f"Exec={bin_path}")
        text = text.replace("Exec=/usr/bin/touchflowd", f"Exec={bin_path}")
        (apps / name).write_text(text, encoding="utf-8")
        log.info("Installed desktop: %s", name)

    icon = project_root / "assets" / "logo.svg"
    if icon.exists():
        shutil.copy2(icon, icons / "com.touchflow.Keyboard.svg")

    return apps / "com.touchflow.Keyboard.Virtual.desktop"


def write_systemd_service(project_root: Path) -> None:
    """Пишет user systemd unit с правильным путём (не /usr/bin)."""
    svc_dir = _home() / ".config" / "systemd" / "user"
    svc_dir.mkdir(parents=True, exist_ok=True)
    bin_path = touchflowd_path()
    wrapper = project_root / "scripts" / "touchflowd-wrapper.sh"
    exec_line = str(wrapper) if wrapper.exists() else bin_path

    content = f"""[Unit]
Description=TouchFlow On-Screen Keyboard
Documentation=https://github.com/eturnercus/keyboard
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart={exec_line}
Restart=on-failure
RestartSec=3
Environment=GTK_USE_PORTAL=0
Environment=GTK_MODULES=gail:atk-bridge
Environment=QT_ACCESSIBILITY=1

[Install]
WantedBy=graphical-session.target
"""
    (svc_dir / "touchflow-daemon.service").write_text(content, encoding="utf-8")


def enable_systemd_service() -> tuple[bool, str]:
    for cmd in (
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "touchflow-daemon.service"],
        ["systemctl", "--user", "restart", "touchflow-daemon.service"],
    ):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 and "enable" in cmd[2]:
            return False, r.stderr or r.stdout
    return True, "systemd service started"


def register_kde_virtual_keyboard(virtual_desktop: Path) -> None:
    """Регистрация в KDE: Параметры системы → Виртуальные клавиатуры."""
    if not virtual_desktop.exists():
        return
    desktop_id = virtual_desktop.name
    log.info("KDE virtual keyboard desktop: %s", desktop_id)

    # kwriteconfig6 / kwriteconfig5 — выставить TouchFlow в kwinrc
    for writer in ("kwriteconfig6", "kwriteconfig5"):
        if not shutil.which(writer):
            continue
        subprocess.run(
            [writer, "--file", "kwinrc", "--group", "Wayland",
             "--key", "InputMethod", str(virtual_desktop)],
            capture_output=True,
        )
        subprocess.run(
            [writer, "--file", "kwinrc", "--group", "Wayland",
             "--key", "VirtualKeyboardEnabled", "true"],
            capture_output=True,
        )
        break

    # Уведомить KWin о смене конфига (Plasma 6 / 5)
    subprocess.run(
        ["busctl", "--user", "emit", "/kwinrc", "org.kde.kconfig.notify",
         "ConfigChanged", "a{saay}", "1", "Wayland", "1", "11",
         "73", "110", "112", "117", "116", "77", "101", "116", "104", "111", "100"],
        capture_output=True,
    )


def register_gnome_screen_keyboard(enable: bool = True) -> None:
    """GNOME: включить экранную клавиатуру в спец. возможностях."""
    if not shutil.which("gsettings"):
        return
    val = "true" if enable else "false"
    subprocess.run(
        ["gsettings", "set", "org.gnome.desktop.a11y.applications",
         "screen-keyboard-enabled", val],
        capture_output=True,
    )
    subprocess.run(
        ["gsettings", "set", "org.gnome.desktop.a11y",
         "always-show-universal-access-status", "true"],
        capture_output=True,
    )


def full_system_register(project_root: Path) -> str:
    """Полная регистрация после установки."""
    virtual = install_desktop_files(project_root)
    write_systemd_service(project_root)
    ok, msg = enable_systemd_service()
    if not ok:
        log.warning("systemd: %s", msg)

    register_kde_virtual_keyboard(virtual)
    register_gnome_screen_keyboard(True)

    hints = [
        "TouchFlow зарегистрирован.",
        "",
        "KDE/Wayland: Параметры системы → Устройства ввода → Виртуальная клавиатура → TouchFlow",
        "GNOME: Настройки → Специальные возможности → Экранная клавиатура",
        "",
        f"Демон: {'запущен' if ok else 'ошибка — см. journalctl --user -u touchflow-daemon'}",
    ]
    return "\n".join(hints)
