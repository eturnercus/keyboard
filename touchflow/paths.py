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
    """Добавить ~/.local/bin в PATH в ~/.profile если нет."""
    bin_dir = str(local_bin_dir())
    line = f'export PATH="{bin_dir}:$PATH"  # TouchFlow'
    profile = home() / ".profile"
    bashrc = home() / ".bashrc"
    changed = False
    for f in (profile, bashrc):
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if bin_dir in text:
            continue
        with f.open("a", encoding="utf-8") as out:
            out.write(f"\n{line}\n")
        changed = True
    if not profile.exists() and not changed:
        profile.write_text(f"{line}\n", encoding="utf-8")
        changed = True
    return changed


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
        names = ("touchflowd", "touchflow-settings", "touchflow-cli")
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

    lines.append("")
    lines.append("OK — всё в порядке" if ok else "ЕСТЬ ПРОБЛЕМЫ — запустите: ./scripts/install.sh")
    return ok, "\n".join(lines)
