"""Надёжное разрешение путей к бинарникам TouchFlow."""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path


def home() -> Path:
    return Path.home()


def local_bin_dir() -> Path:
    return home() / ".local" / "bin"


def local_apps_dir() -> Path:
    return home() / ".local" / "share" / "applications"


def ensure_local_bin() -> Path:
    d = local_bin_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def resolve_cmd(name: str) -> str:
    """Абсолютный путь к команде; приоритет ~/.local/bin."""
    local = ensure_local_bin() / name
    if local.exists() and os.access(local, os.X_OK):
        return str(local)
    found = shutil.which(name)
    if found:
        return found
    # pip user scripts on some systems
    for candidate in (
        home() / ".local" / "bin" / name,
        Path(sys.executable).parent / name,
    ):
        if candidate.exists():
            return str(candidate)
    return str(local)


def ensure_path_in_shell_profile() -> bool:
    """Добавить ~/.local/bin в PATH (shell, systemd user env, KDE)."""
    bin_dir = str(local_bin_dir())
    line = f'export PATH="{bin_dir}:$PATH"  # TouchFlow'
    changed = False

    for f in (home() / ".profile", home() / ".bashrc"):
        if f.exists():
            text = f.read_text(encoding="utf-8", errors="replace")
            if bin_dir not in text:
                with f.open("a", encoding="utf-8") as out:
                    out.write(f"\n{line}\n")
                changed = True
        elif f.name == ".profile":
            f.write_text(f"{line}\n", encoding="utf-8")
            changed = True

    # systemd --user (KDE Wayland, GNOME)
    env_d = home() / ".config" / "environment.d"
    env_d.mkdir(parents=True, exist_ok=True)
    env_file = env_d / "99-touchflow.conf"
    env_content = f'PATH="{bin_dir}:$PATH"\n'
    if not env_file.exists() or env_file.read_text(encoding="utf-8") != env_content:
        env_file.write_text(env_content, encoding="utf-8")
        changed = True

    # KDE Plasma
    plasma_env = home() / ".config" / "plasma-workspace" / "env"
    plasma_env.mkdir(parents=True, exist_ok=True)
    plasma_script = plasma_env / "touchflow.sh"
    plasma_content = f'#!/bin/sh\nexport PATH="{bin_dir}:$PATH"\n'
    if not plasma_script.exists() or plasma_script.read_text(encoding="utf-8") != plasma_content:
        plasma_script.write_text(plasma_content, encoding="utf-8")
        plasma_script.chmod(0o755)
        changed = True

    return changed


def fix_gtk4_settings_ini() -> bool:
    """Убрать gtk-modules из gtk-4.0/settings.ini (ломает GTK4)."""
    ini = home() / ".config" / "gtk-4.0" / "settings.ini"
    if not ini.exists():
        return False
    lines = ini.read_text(encoding="utf-8", errors="replace").splitlines()
    new_lines = [ln for ln in lines if not ln.strip().startswith("gtk-modules")]
    if len(new_lines) == len(lines):
        return False
    ini.write_text("\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8")
    return True


def patch_desktop_file(content: str) -> str:
    """Подставить абсолютные пути во все Exec= строки."""
    mapping = [
        ("Exec=touchflow-settings-cpp", f"Exec={resolve_cmd('touchflow-settings-cpp')}"),
        ("Exec=touchflow-settings", f"Exec={resolve_cmd('touchflow-settings')}"),
        ("Exec=touchflow-cli", f"Exec={resolve_cmd('touchflow-cli')}"),
        ("Exec=touchflowd-cpp --virtual-keyboard", f"Exec={resolve_cmd('touchflowd-cpp')} --virtual-keyboard"),
        ("Exec=touchflowd --virtual-keyboard", f"Exec={resolve_cmd('touchflowd')} --virtual-keyboard"),
        ("Exec=touchflowd-cpp", f"Exec={resolve_cmd('touchflowd-cpp')}"),
        ("Exec=touchflowd", f"Exec={resolve_cmd('touchflowd')}"),
        ("Exec=/usr/bin/touchflowd", f"Exec={resolve_cmd('touchflowd')}"),
    ]
    for old, new in mapping:
        content = content.replace(old, new)
    return content


def symlink_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        dst.symlink_to(src.resolve())
    except OSError:
        shutil.copy2(src, dst)
        dst.chmod(dst.stat().st_mode | stat.S_IEXEC)


def install_dbus_service() -> Path:
    """D-Bus activation: автозапуск touchflowd при обращении к com.touchflow.Keyboard."""
    svc_dir = home() / ".local" / "share" / "dbus-1" / "services"
    svc_dir.mkdir(parents=True, exist_ok=True)
    dst = svc_dir / "com.touchflow.Keyboard.service"
    template = (Path(__file__).resolve().parent.parent / "data" / "com.touchflow.Keyboard.service")
    if template.exists():
        text = template.read_text(encoding="utf-8")
    else:
        text = "[D-BUS Service]\nName=com.touchflow.Keyboard\nExec=TOUCHFLOWD_PATH\n"
    text = text.replace("TOUCHFLOWD_PATH", resolve_cmd("touchflowd"))
    dst.write_text(text, encoding="utf-8")
    return dst


def remove_dbus_service() -> None:
    svc = home() / ".local" / "share" / "dbus-1" / "services" / "com.touchflow.Keyboard.service"
    if svc.exists():
        svc.unlink()


def ensure_pip_scripts(names: tuple[str, ...] = ()) -> list[str]:
    """Скопировать/связать entry points в ~/.local/bin после pip install."""
    if not names:
        names = ("touchflowd", "touchflow-settings", "touchflow-cli", "touchflow-doctor", "touchflow-installer")
    ensure_local_bin()
    installed: list[str] = []
    for name in names:
        dst = local_bin_dir() / name
        src_path = shutil.which(name)
        if src_path and Path(src_path).resolve() != dst.resolve():
            symlink_or_copy(Path(src_path), dst)
            installed.append(str(dst))
        elif dst.exists():
            installed.append(str(dst))
    return installed


def doctor_report() -> tuple[bool, str]:
    """Проверка установки; возвращает (ok, текст)."""
    import subprocess

    from touchflow.external_kb import has_builtin_keyboard, has_pluggable_keyboard

    lines: list[str] = ["=== TouchFlow Doctor ===", ""]
    ok = True
    warnings: list[str] = []

    bin_dir = local_bin_dir()
    lines.append(f"~/.local/bin: {bin_dir} {'✓' if bin_dir.is_dir() else '✗'}")
    if not bin_dir.is_dir():
        ok = False

    path_ok = str(bin_dir) in os.environ.get("PATH", "")
    lines.append(f"PATH содержит ~/.local/bin: {'✓' if path_ok else '⚠ добавьте или перелогиньтесь'}")

    for name in ("touchflowd", "touchflow-settings", "touchflow-cli"):
        p = resolve_cmd(name)
        exists = Path(p).exists()
        lines.append(f"  {name}: {p} {'✓' if exists else '✗ НЕ НАЙДЕН'}")
        if not exists:
            ok = False

    cpp = resolve_cmd("touchflowd-cpp")
    if Path(cpp).exists():
        lines.append(f"  touchflowd-cpp: {cpp} ✓ (C++)")
        if Path(resolve_cmd("touchflow-settings-cpp")).exists():
            lines.append("  touchflow-settings-cpp: ✓")

    svc = home() / ".config/systemd/user/touchflow-daemon.service"
    lines.append(f"\nsystemd unit: {'✓' if svc.exists() else '— не установлен'}")

    daemon_active = False
    if shutil.which("systemctl"):
        r = subprocess.run(
            ["systemctl", "--user", "is-active", "touchflow-daemon"],
            capture_output=True,
            text=True,
        )
        daemon_active = r.returncode == 0 and r.stdout.strip() == "active"
        lines.append(f"демон запущен: {'✓' if daemon_active else '✗ НЕ ЗАПУЩЕН'}")
        if not daemon_active:
            ok = False
            warnings.append("  БЕЗ sudo: systemctl --user restart touchflow-daemon")
            warnings.append("  journalctl --user -u touchflow-daemon -e")

    dbus_svc = home() / ".local" / "share" / "dbus-1" / "services" / "com.touchflow.Keyboard.service"
    lines.append(f"D-Bus activation: {'✓' if dbus_svc.exists() else '✗'}")
    if not dbus_svc.exists():
        ok = False
        warnings.append("  Переустановите: curl ... | bash")

    dbus_ok = False
    dbus_visible = False
    try:
        from touchflow.dbus_client import dbus_status

        st = dbus_status()
        dbus_ok = True
        dbus_visible = bool(st["visible"])
        lines.append(
            f"D-Bus: ✓ v{st['version']}, видима={'да' if dbus_visible else 'нет'}, "
            f"USB/BT клавиатура={'да' if st['external_keyboard'] else 'нет'}"
        )
    except Exception as e:
        lines.append(f"D-Bus: ✗ недоступен ({e})")
        if daemon_active:
            ok = False

    atspi_sock = Path(f"/run/user/{os.getuid()}/at-spi/bus")
    lines.append(f"AT-SPI bus: {'✓' if atspi_sock.exists() else '✗ нет сокета'}")
    if not atspi_sock.exists():
        ok = False
        warnings.append("  sudo apt install at-spi2-core dbus-x11 && перелогин")

    atspi_py = False
    try:
        import gi

        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi  # noqa: F401

        atspi_py = True
    except (ImportError, ValueError):
        pass
    lines.append(f"AT-SPI Python: {'✓' if atspi_py else '✗ python3-atspi / gir1.2-atspi-2.0'}")
    if not atspi_py:
        ok = False

    layer_shell = False
    try:
        import gi

        gi.require_version("Gtk4LayerShell", "1.0")
        from gi.repository import Gtk4LayerShell  # noqa: F401

        layer_shell = True
    except (ImportError, ValueError):
        pass
    lines.append(
        f"gtk4-layer-shell: {'✓' if layer_shell else '⚠ рекомендуется на Wayland (gir1.2-layer-shell-0)'}"
    )

    session = os.environ.get("XDG_SESSION_TYPE", "?")
    lines.append(f"Сессия: {session}")
    if session == "x11":
        warnings.append("  KDE виртуальная клавиатура работает только на Wayland")

    virtual = local_apps_dir() / "com.touchflow.Keyboard.Virtual.desktop"
    lines.append(f"KDE desktop: {'✓' if virtual.exists() else '✗'}")
    if not virtual.exists():
        ok = False

    kde_im = ""
    for reader in ("kreadconfig6", "kreadconfig5"):
        if shutil.which(reader):
            r = subprocess.run(
                [reader, "--file", "kwinrc", "--group", "Wayland", "--key", "InputMethod"],
                capture_output=True,
                text=True,
            )
            kde_im = (r.stdout or "").strip()
            break
    if kde_im:
        touchflow_selected = "touchflow" in kde_im.lower()
        lines.append(f"KDE InputMethod: {kde_im} {'✓' if touchflow_selected else '⚠ выберите TouchFlow в настройках'}")
        if not touchflow_selected:
            warnings.append("  KDE: Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow")
    elif session == "wayland":
        lines.append("KDE InputMethod: — (не KDE или kreadconfig недоступен)")

    settings_desktop = local_apps_dir() / "com.touchflow.Settings.desktop"
    if settings_desktop.exists():
        text = settings_desktop.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("Exec="):
                exec_val = line[5:].strip()
                abs_ok = exec_val.startswith("/") and "touchflow-settings" in exec_val
                lines.append(f"Settings desktop: {'✓' if abs_ok else '✗ Exec без полного пути'}")
                if not abs_ok:
                    ok = False
                break
    else:
        lines.append("Settings desktop: ✗")
        ok = False

    if os.access("/dev/uinput", os.W_OK):
        lines.append("\nuinput: ✓")
    else:
        lines.append("\nuinput: ⚠ нет доступа — sudo usermod -aG input $USER && перелогин")
        ok = False

    if has_pluggable_keyboard():
        lines.append("USB/BT клавиатура: подключена (авто-показ отключён при «Скрывать при внешней клавиатуре»)")
        warnings.append("  Показ вручную: touchflow-cli show или кнопка в настройках")
    elif has_builtin_keyboard():
        lines.append("Встроенная клавиатура: есть (не блокирует авто-показ)")

    gtk_ini = home() / ".config" / "gtk-4.0" / "settings.ini"
    if gtk_ini.exists() and "gtk-modules" in gtk_ini.read_text(encoding="utf-8", errors="replace"):
        lines.append("\ngtk-4.0/settings.ini: ⚠ удалите gtk-modules (touchflow-doctor --fix)")

    if dbus_ok and not dbus_visible:
        warnings.append("  Показать сейчас: touchflow-cli show")

    if not path_ok:
        lines.append(f"\nДля текущего терминала: export PATH=\"{bin_dir}:$PATH\"")
        lines.append("Или перелогиньтесь / перезапустите KDE")

    if warnings:
        lines.append("\nПодсказки:")
        lines.extend(warnings)

    lines.append("")
    lines.append("OK — всё в порядке" if ok else "ЕСТЬ ПРОБЛЕМЫ — см. выше")
    return ok, "\n".join(lines)
