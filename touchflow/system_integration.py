"""Интеграция с системными настройками (KDE, GNOME, systemd)."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from touchflow.paths import (
    ensure_local_bin,
    ensure_path_in_shell_profile,
    ensure_pip_scripts,
    local_apps_dir,
    patch_desktop_file,
    resolve_cmd,
)

log = logging.getLogger(__name__)

DESKTOP_FILES = (
    "com.touchflow.Settings.desktop",
    "com.touchflow.Keyboard.desktop",
    "com.touchflow.Keyboard.Virtual.desktop",
)


def _home() -> Path:
    return Path.home()


def touchflowd_path() -> str:
    return resolve_cmd("touchflowd")


def install_desktop_files(project_root: Path) -> Path:
    apps = local_apps_dir()
    icons = _home() / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps"
    apps.mkdir(parents=True, exist_ok=True)
    icons.mkdir(parents=True, exist_ok=True)

    ensure_pip_scripts()

    for name in DESKTOP_FILES:
        src = project_root / "data" / name
        if not src.exists():
            continue
        text = patch_desktop_file(src.read_text(encoding="utf-8"))
        (apps / name).write_text(text, encoding="utf-8")
        log.info("Installed desktop: %s", name)

    icon = project_root / "assets" / "logo.svg"
    if icon.exists():
        shutil.copy2(icon, icons / "com.touchflow.Keyboard.svg")

    return apps / "com.touchflow.Keyboard.Virtual.desktop"


def write_systemd_service(project_root: Path) -> None:
    """Пишет user systemd unit с абсолютным путём."""
    svc_dir = _home() / ".config" / "systemd" / "user"
    svc_dir.mkdir(parents=True, exist_ok=True)
    bin_path = resolve_cmd("touchflowd")

    content = f"""[Unit]
Description=TouchFlow On-Screen Keyboard (Python)
Documentation=https://github.com/eturnercus/keyboard
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart={bin_path}
Restart=on-failure
RestartSec=3
Environment=GTK_USE_PORTAL=0
Environment=AT_SPI_BUS_ADDRESS=unix:path=/run/user/%U/at-spi/bus

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
        if r.returncode != 0 and len(cmd) > 2 and cmd[2] == "enable":
            return False, r.stderr or r.stdout
    return True, "systemd service started"


def verify_daemon_runtime() -> tuple[bool, str]:
    """Проверка что демон отвечает по D-Bus после установки."""
    import time

    time.sleep(2)
    r = subprocess.run(
        ["systemctl", "--user", "is-active", "touchflow-daemon"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or r.stdout.strip() != "active":
        return False, "демон не запущен (journalctl --user -u touchflow-daemon -e)"
    try:
        from touchflow.dbus_client import dbus_show, dbus_status

        st = dbus_status()
        dbus_show()
        return True, f"D-Bus OK (v{st['version']}), тест показа клавиатуры отправлен"
    except Exception as e:
        return False, f"D-Bus недоступен: {e}"


def register_kde_virtual_keyboard(virtual_desktop: Path) -> None:
    """Регистрация в KDE: Параметры системы → Виртуальные клавиатуры."""
    if not virtual_desktop.exists():
        return
    desktop_id = virtual_desktop.name
    log.info("KDE virtual keyboard desktop: %s", desktop_id)

    for writer in ("kwriteconfig6", "kwriteconfig5"):
        if not shutil.which(writer):
            continue
        subprocess.run(
            [writer, "--file", "kwinrc", "--group", "Wayland",
             "--key", "InputMethod", desktop_id],
            capture_output=True,
        )
        subprocess.run(
            [writer, "--file", "kwinrc", "--group", "Wayland",
             "--key", "VirtualKeyboardEnabled", "true"],
            capture_output=True,
        )
        break

    subprocess.run(
        ["busctl", "--user", "emit", "/kwinrc", "org.kde.kconfig.notify",
         "ConfigChanged", "a{saay}", "1", "Wayland", "1", "11",
         "73", "110", "112", "117", "116", "77", "101", "116", "104", "111", "100"],
        capture_output=True,
    )


def register_gnome_screen_keyboard(enable: bool = True) -> None:
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
    ensure_local_bin()
    ensure_path_in_shell_profile()
    ensure_pip_scripts()
    try:
        from touchflow.paths import fix_gtk4_settings_ini
        if fix_gtk4_settings_ini():
            log.info("Removed gtk-modules from gtk-4.0/settings.ini")
    except Exception:
        pass

    virtual = install_desktop_files(project_root)
    write_systemd_service(project_root)
    ok, msg = enable_systemd_service()
    if not ok:
        log.warning("systemd: %s", msg)

    runtime_ok, runtime_msg = verify_daemon_runtime()
    if not runtime_ok:
        log.warning("Runtime check: %s", runtime_msg)

    register_kde_virtual_keyboard(virtual)
    register_gnome_screen_keyboard(True)

    subprocess.run(
        ["update-desktop-database", str(local_apps_dir())],
        capture_output=True,
    )
    for cmd in (["kbuildsycoca6", "--noincremental"], ["kbuildsycoca5", "--noincremental"]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, capture_output=True)
            break

    from touchflow.paths import doctor_report
    _, doctor = doctor_report()

    hints = [
        "TouchFlow зарегистрирован.",
        "",
        f"Настройки: {resolve_cmd('touchflow-settings')}",
        f"Проверка: touchflow-doctor",
        "",
        "KDE/Wayland: Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow",
        "",
        f"Демон: {'запущен' if ok else 'ошибка — journalctl --user -u touchflow-daemon'}",
        f"Проверка D-Bus: {runtime_msg}",
        "",
        "Показать клавиатуру: touchflow-cli show  или кнопка в настройках",
        "",
        doctor,
    ]
    return "\n".join(hints)
