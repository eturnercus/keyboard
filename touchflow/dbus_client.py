"""Клиент D-Bus для управления демоном TouchFlow."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

log = logging.getLogger(__name__)

DBUS_BUS = "com.touchflow.Keyboard"
DBUS_PATH = "/com/touchflow/Keyboard"

_DAEMON_START_HINT = (
    "Демон не запущен. Выполните БЕЗ sudo:\n"
    "  systemctl --user restart touchflow-daemon\n"
    "или:\n"
    "  touchflow-cli show"
)


def _session_bus():
    from pydbus import SessionBus

    return SessionBus()


def dbus_proxy():
    return _session_bus().get(DBUS_BUS, DBUS_PATH)


def dbus_available() -> bool:
    try:
        dbus_proxy()
        return True
    except Exception:
        return False


def _touchflowd_path() -> str:
    from touchflow.paths import resolve_cmd

    return resolve_cmd("touchflowd")


def ensure_daemon_running(wait_seconds: float = 12.0) -> None:
    """Запустить демон если D-Bus недоступен (systemd → прямой spawn → D-Bus activation)."""
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

    # D-Bus activation (.service file) — запрос имени запускает touchflowd
    try:
        _session_bus().get(DBUS_BUS, DBUS_PATH)
        if dbus_available():
            return
    except Exception as e:
        log.debug("D-Bus activation failed: %s", e)

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
    getattr(dbus_proxy(), method)(*args)


def dbus_show() -> None:
    dbus_call("Show")


def dbus_hide() -> None:
    dbus_call("Hide")


def dbus_toggle() -> None:
    dbus_call("Toggle")


def dbus_status() -> dict[str, object]:
    """Состояние демона через D-Bus; исключение если недоступен."""
    ensure_daemon_running()
    proxy = dbus_proxy()
    return {
        "version": str(proxy.Version),
        "visible": bool(proxy.Visible),
        "external_keyboard": bool(proxy.ExternalKeyboardConnected),
    }


def try_show_existing_daemon() -> bool:
    """Если демон уже запущен — показать клавиатуру и вернуть True."""
    try:
        if not dbus_available():
            return False
        getattr(dbus_proxy(), "Show")()
        return True
    except Exception as e:
        log.debug("No running daemon to show: %s", e)
        return False
