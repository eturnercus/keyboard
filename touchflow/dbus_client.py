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


def _dbus_python_iface():
    import dbus

    bus = dbus.SessionBus()
    obj = bus.get_object(DBUS_BUS, DBUS_PATH)
    return dbus.Interface(obj, DBUS_INTERFACE)


def _dbus_python_props():
    import dbus

    bus = dbus.SessionBus()
    obj = bus.get_object(DBUS_BUS, DBUS_PATH)
    return dbus.Interface(obj, dbus.PROPERTIES_IFACE)


def _pydbus_proxy():
    from pydbus import SessionBus

    return SessionBus().get(DBUS_BUS, DBUS_PATH, DBUS_INTERFACE)


def _call_method(method: str, *args) -> None:
    """Вызов метода D-Bus через dbus-python (приоритет) или pydbus."""
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
    try:
        _get_property("Version")
        return True
    except Exception:
        return False


def ensure_daemon_running(wait_seconds: float = 12.0) -> None:
    """Запустить демон если D-Bus недоступен (systemd → прямой spawn)."""
    if dbus_available():
        return

    env = os.environ.copy()
    uid = os.getuid()
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")

    if shutil.which("systemctl"):
        subprocess.run(
            ["systemctl", "--user", "start", "touchflow-daemon"],
            capture_output=True,
            text=True,
            env=env,
        )
        if _wait_for_dbus(wait_seconds / 2):
            return

    touchflowd = _touchflowd_path()
    if Path(touchflowd).exists():
        subprocess.Popen(
            [touchflowd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=env,
        )
        if _wait_for_dbus(wait_seconds / 2):
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
