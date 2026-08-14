"""Графический установщик TouchFlow — запускается из AppImage."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

from touchflow import __version__

log = logging.getLogger("touchflow-installer")

# Корень проекта
if os.environ.get("PROJECT_ROOT"):
    PROJECT_ROOT = Path(os.environ["PROJECT_ROOT"])
elif os.environ.get("APPIMAGE"):
    PROJECT_ROOT = Path(os.environ["APPIMAGE"]).parent / "usr" / "share" / "touchflow"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEBIAN_PACKAGES = [
    "python3", "python3-gi", "python3-gi-cairo", "python3-pip",
    "gir1.2-gtk-4.0", "gir1.2-adw-1", "gir1.2-atspi-2.0",
    "python3-evdev", "at-spi2-core", "dbus-x11",
]

PIP_PACKAGES = ["pydbus", "tomli-w"]


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def detect_pkg_manager() -> str:
    if shutil.which("apt-get"):
        return "apt"
    if shutil.which("dnf"):
        return "dnf"
    if shutil.which("pacman"):
        return "pacman"
    return "unknown"


def install_system_deps(pkg_mgr: str) -> tuple[bool, str]:
    if pkg_mgr == "apt":
        r = _run(["sudo", "apt-get", "update", "-qq"])
        if r.returncode != 0:
            return False, r.stderr or r.stdout
        r = _run(["sudo", "apt-get", "install", "-y"] + DEBIAN_PACKAGES)
        return r.returncode == 0, r.stderr or r.stdout
    if pkg_mgr == "dnf":
        r = _run(["sudo", "dnf", "install", "-y", "python3-gobject", "gtk4", "libadwaita", "at-spi2-core", "python3-evdev"])
        return r.returncode == 0, r.stderr or r.stdout
    if pkg_mgr == "pacman":
        r = _run(["sudo", "pacman", "-S", "--noconfirm", "--needed", "python", "python-gobject", "gtk4", "libadwaita", "at-spi2-core", "python-evdev"])
        return r.returncode == 0, r.stderr or r.stdout
    return True, "Менеджер пакетов не обнаружен — пропуск системных зависимостей"


def install_touchflow(log_cb) -> tuple[bool, str]:
    from touchflow.system_integration import full_system_register

    home = Path.home()
    local_bin = home / ".local" / "bin"
    local_share = home / ".local" / "share"
    apps_dir = local_share / "applications"
    icons_dir = local_share / "icons" / "hicolor" / "scalable" / "apps"
    systemd_dir = home / ".config" / "systemd" / "user"

    for d in (local_bin, apps_dir, icons_dir, systemd_dir):
        d.mkdir(parents=True, exist_ok=True)

    log_cb("Установка Python-пакета...")
    r = _run([sys.executable, "-m", "pip", "install", "--user", str(PROJECT_ROOT)])
    if r.returncode != 0:
        r = _run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", str(PROJECT_ROOT)])
    if r.returncode != 0:
        return False, f"pip install failed:\n{r.stderr}"

    # Копируем wrapper
    wrapper_src = PROJECT_ROOT / "scripts" / "touchflowd-wrapper.sh"
    if wrapper_src.exists():
        wrapper_dst = local_bin / "touchflowd-wrapper"
        shutil.copy2(wrapper_src, wrapper_dst)
        wrapper_dst.chmod(0o755)

    log_cb("Регистрация в системе (KDE, GNOME, systemd)...")
    try:
        hints = full_system_register(PROJECT_ROOT)
        log_cb(hints)
    except Exception as e:
        log_cb(f"Предупреждение регистрации: {e}")
        # fallback
        for name in ("com.touchflow.Settings.desktop", "com.touchflow.Keyboard.desktop",
                      "com.touchflow.Keyboard.Virtual.desktop"):
            src = PROJECT_ROOT / "data" / name
            if src.exists():
                shutil.copy2(src, apps_dir / name)

    log_cb("Добавление в группу input...")
    user = os.environ.get("USER", "")
    if user:
        _run(["sudo", "usermod", "-aG", "input", user])

    log_cb("Готово!")
    from touchflow.paths import doctor_report, resolve_cmd
    _, doctor = doctor_report()
    return True, (
        "TouchFlow установлен!\n\n"
        f"• Настройки: {resolve_cmd('touchflow-settings')}\n"
        "• Проверка: touchflow-doctor\n"
        "• KDE: Параметры → Виртуальная клавиатура → TouchFlow\n"
        "• Перелогиньтесь для группы input\n\n"
        f"{doctor}"
    )


class InstallerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.touchflow.Installer")
        self._log_buffer = ""
        self._step = 0

    def do_activate(self):
        win = Adw.ApplicationWindow(application=self)
        win.set_title("TouchFlow — Установка")
        win.set_default_size(560, 480)

        header = Adw.HeaderBar()
        win.set_titlebar(header)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        title = Gtk.Label(label="TouchFlow Keyboard")
        title.add_css_class("title-1")
        box.append(title)

        self._subtitle = Gtk.Label(label=f"Версия {__version__} — установщик")
        self._subtitle.add_css_class("dim-label")
        box.append(self._subtitle)

        self._info = Gtk.Label(
            label="Этот установщик поставит экранную клавиатуру TouchFlow:\n"
            "• демон touchflowd (автозапуск)\n"
            "• настройки touchflow-settings\n"
            "• быстрые кнопки: копировать, вставить, вырезать и др.",
            xalign=0,
            justify=Gtk.Justification.LEFT,
        )
        box.append(self._info)

        self._progress = Gtk.ProgressBar(show_text=True)
        self._progress.set_visible(False)
        box.append(self._progress)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(120)
        self._log_view = Gtk.TextView()
        self._log_view.set_editable(False)
        self._log_view.set_monospace(True)
        self._log_view.add_css_class("monospace")
        scrolled.set_child(self._log_view)
        scrolled.set_visible(False)
        self._log_scrolled = scrolled
        box.append(scrolled)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)

        self._cancel_btn = Gtk.Button(label="Отмена")
        self._cancel_btn.connect("clicked", lambda *_: win.close())
        btn_box.append(self._cancel_btn)

        self._install_btn = Gtk.Button(label="Установить")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.connect("clicked", self._on_install)
        btn_box.append(self._install_btn)

        self._settings_btn = Gtk.Button(label="Открыть настройки")
        self._settings_btn.set_visible(False)
        self._settings_btn.connect("clicked", self._open_settings)
        btn_box.append(self._settings_btn)

        box.append(btn_box)
        win.set_content(box)
        win.present()

    def _append_log(self, text: str) -> None:
        self._log_buffer += text + "\n"
        buf = self._log_view.get_buffer()
        buf.set_text(self._log_buffer)
        mark = buf.get_end_iter()
        self._log_view.scroll_to_iter(mark, 0.0, False, 0.0, 0.0)

    def _on_install(self, *_):
        self._install_btn.set_sensitive(False)
        self._cancel_btn.set_sensitive(False)
        self._progress.set_visible(True)
        self._log_scrolled.set_visible(True)
        self._progress.set_fraction(0.1)
        self._progress.set_text("Проверка...")
        GLib.idle_add(self._do_install)

    def _do_install(self) -> bool:
        self._append_log("=== TouchFlow Installer ===")
        pkg = detect_pkg_manager()
        self._append_log(f"Менеджер пакетов: {pkg}")
        self._progress.set_fraction(0.2)

        self._append_log("Установка системных зависимостей...")
        ok, msg = install_system_deps(pkg)
        self._append_log(msg[:500] if msg else ("OK" if ok else "FAILED"))
        self._progress.set_fraction(0.5)

        for pkg in PIP_PACKAGES:
            self._append_log(f"pip: {pkg}")
            _run([sys.executable, "-m", "pip", "install", "--user", pkg])

        def log_cb(t):
            GLib.idle_add(self._append_log, t)

        ok, msg = install_touchflow(log_cb)
        self._append_log(msg)
        self._progress.set_fraction(1.0)
        self._progress.set_text("Готово!" if ok else "Ошибка")

        if ok:
            self._install_btn.set_label("Установлено ✓")
            self._settings_btn.set_visible(True)
            self._cancel_btn.set_label("Закрыть")
            self._cancel_btn.set_sensitive(True)
        else:
            self._install_btn.set_sensitive(True)
            self._install_btn.set_label("Повторить")
            self._cancel_btn.set_sensitive(True)
        return False

    def _open_settings(self, *_):
        local_bin = Path.home() / ".local" / "bin"
        settings = shutil.which("touchflow-settings") or str(local_bin / "touchflow-settings")
        subprocess.Popen([settings])


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        app = InstallerApp()
        sys.exit(app.run(sys.argv))
    except Exception as e:
        msg = (
            f"Не удалось запустить установщик:\n{e}\n\n"
            "Установите зависимости:\n"
            "  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1\n\n"
            "Или используйте shell-установщик:\n"
            "  curl -fsSL .../touchflow-install.sh | bash"
        )
        print(msg, file=sys.stderr)
        if shutil.which("zenity"):
            subprocess.run(["zenity", "--error", "--text", msg, "--width", "400"])
        sys.exit(1)
