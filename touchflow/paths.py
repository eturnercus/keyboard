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
    lines: list[str] = ["=== TouchFlow Doctor ===", ""]
    ok = True

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
            lines.append(f"  touchflow-settings-cpp: ✓")

    svc = home() / ".config/systemd/user/touchflow-daemon.service"
    lines.append(f"\nsystemd (Python): {'✓' if svc.exists() else '— не установлен'}")

    virtual = local_apps_dir() / "com.touchflow.Keyboard.Virtual.desktop"
    lines.append(f"KDE desktop: {'✓' if virtual.exists() else '✗'}")
    if not virtual.exists():
        ok = False

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

    gtk_ini = home() / ".config" / "gtk-4.0" / "settings.ini"
    if gtk_ini.exists() and "gtk-modules" in gtk_ini.read_text(encoding="utf-8", errors="replace"):
        lines.append("\ngtk-4.0/settings.ini: ⚠ удалите gtk-modules (touchflow-doctor --fix)")

    if not path_ok:
        lines.append(f"\nДля текущего терминала: export PATH=\"{bin_dir}:$PATH\"")
        lines.append("Или перелогиньтесь / перезапустите KDE")

    lines.append("")
    lines.append("OK — всё в порядке" if ok else "ЕСТЬ ПРОБЛЕМЫ — запустите: ./scripts/install.sh")
    return ok, "\n".join(lines)
