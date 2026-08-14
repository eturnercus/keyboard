"""Клиент D-Bus для управления демоном TouchFlow."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

from touchflow.dbus_iface import DBUS_BUS, DBUS_INTERFACE, DBUS_PATH

log = logging.getLogger(__name__)

_DAEMON_START_HINT = (
    "Демон не запущен. Выполните БЕЗ sudo:\n"
    "  systemctl --user restart touchflow-daemon\n"
    "или:\n"
    "  touchflow-cli show"
)


def _touchflowd_path() -> str:
    from touchflow.paths import resolve_cmd

    return resolve_cmd("touchflowd")


def _session_bus():
    import dbus

    return dbus.SessionBus()


def _name_on_bus() -> bool:
    """Проверить well-known имя без D-Bus activation (избегает зависания)."""
    try:
        import dbus

        return bool(_session_bus().name_has_owner(DBUS_BUS))
    except Exception as e:
        log.debug("name_has_owner failed: %s", e)
        return False


def _dbus_python_iface():
    import dbus

    bus = _session_bus()
    if not bus.name_has_owner(DBUS_BUS):
        raise RuntimeError(f"D-Bus name {DBUS_BUS} not on session bus")
    obj = bus.get_object(DBUS_BUS, DBUS_PATH)
    return dbus.Interface(obj, DBUS_INTERFACE)


def _dbus_python_props():
    import dbus

    bus = _session_bus()
    if not bus.name_has_owner(DBUS_BUS):
        raise RuntimeError(f"D-Bus name {DBUS_BUS} not on session bus")
    obj = bus.get_object(DBUS_BUS, DBUS_PATH)
    return dbus.Interface(obj, dbus.PROPERTIES_IFACE)


def _pydbus_proxy():
    from pydbus import SessionBus

    return SessionBus().get(DBUS_BUS, DBUS_PATH, DBUS_INTERFACE)


def _call_method(method: str, *args) -> None:
    """Вызов метода D-Bus через dbus-python (приоритет) или pydbus."""
    if not _name_on_bus():
        raise RuntimeError(_DAEMON_START_HINT)

    try:
        import dbus  # noqa: F401

        iface = _dbus_python_iface()
        getattr(iface, method)(*args)
        return
    except ImportError:
        pass
    except Exception as e:
        if "ServiceUnknown" in str(e) or "was not provided" in str(e):
            raise
        log.debug("dbus-python call failed, trying pydbus: %s", e)

    proxy = _pydbus_proxy()
    getattr(proxy, method)(*args)


def _get_property(name: str):
    if not _name_on_bus():
        raise RuntimeError(_DAEMON_START_HINT)

    try:
        import dbus

        props = _dbus_python_props()
        return props.Get(DBUS_INTERFACE, name)
    except ImportError:
        pass
    except Exception as e:
        log.debug("dbus-python property failed, trying pydbus: %s", e)

    proxy = _pydbus_proxy()
    return getattr(proxy, name)


def dbus_available() -> bool:
    return _name_on_bus()


def _systemd_active() -> bool:
    if not shutil.which("systemctl"):
        return False
    r = subprocess.run(
        ["systemctl", "--user", "is-active", "touchflow-daemon"],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0 and r.stdout.strip() == "active"


def _journal_hint() -> str:
    r = subprocess.run(
        ["journalctl", "--user", "-u", "touchflow-daemon", "-n", "2", "--no-pager"],
        capture_output=True,
        text=True,
    )
    lines = [ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()]
    return lines[-1] if lines else "journalctl --user -u touchflow-daemon -e"


def ensure_daemon_running(wait_seconds: float = 15.0) -> None:
    """Запустить демон если D-Bus недоступен (systemd → прямой spawn)."""
    if dbus_available():
        return

    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")

    if shutil.which("systemctl"):
        subprocess.run(
            ["systemctl", "--user", "import-environment", "WAYLAND_DISPLAY", "DISPLAY", "XDG_CURRENT_DESKTOP"],
            capture_output=True,
            text=True,
            env=env,
        )
        if not _systemd_active():
            subprocess.run(
                ["systemctl", "--user", "start", "touchflow-daemon"],
                capture_output=True,
                text=True,
                env=env,
            )
        if _wait_for_dbus(wait_seconds):
            return

    if _systemd_active():
        raise RuntimeError(
            "Демон active, но D-Bus не зарегистрирован.\n"
            f"  {_journal_hint()}\n"
            "  systemctl --user restart touchflow-daemon"
        )

    touchflowd = _touchflowd_path()
    if Path(touchflowd).exists():
        subprocess.Popen(
            [touchflowd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=env,
        )
        if _wait_for_dbus(min(wait_seconds, 8.0)):
            return

    raise RuntimeError(_DAEMON_START_HINT)


def _wait_for_dbus(seconds: float) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if dbus_available():
            return True
        time.sleep(0.25)
    return False


def dbus_call(method: str, *args) -> None:
    ensure_daemon_running()
    _call_method(method, *args)


def dbus_show() -> None:
    dbus_call("Show")


def dbus_hide() -> None:
    dbus_call("Hide")


def dbus_toggle() -> None:
    dbus_call("Toggle")


def dbus_status() -> dict[str, object]:
    ensure_daemon_running()
    return {
        "version": str(_get_property("Version")),
        "visible": bool(_get_property("Visible")),
        "external_keyboard": bool(_get_property("ExternalKeyboardConnected")),
    }


def try_show_existing_daemon() -> bool:
    try:
        if not dbus_available():
            return False
        _call_method("Show")
        return True
    except Exception as e:
        log.debug("No running daemon to show: %s", e)
        return False
