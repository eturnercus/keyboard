"""Клиент D-Bus для управления демоном TouchFlow."""

from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)

DBUS_BUS = "com.touchflow.Keyboard"
DBUS_PATH = "/com/touchflow/Keyboard"


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


def dbus_call(method: str, *args) -> None:
    getattr(dbus_proxy(), method)(*args)


def dbus_show() -> None:
    dbus_call("Show")


def dbus_hide() -> None:
    dbus_call("Hide")


def dbus_toggle() -> None:
    dbus_call("Toggle")


def dbus_status() -> dict[str, object]:
    """Состояние демона через D-Bus; исключение если недоступен."""
    proxy = dbus_proxy()
    return {
        "version": str(proxy.Version),
        "visible": bool(proxy.Visible),
        "external_keyboard": bool(proxy.ExternalKeyboardConnected),
    }


def try_show_existing_daemon() -> bool:
    """Если демон уже запущен — показать клавиатуру и вернуть True."""
    try:
        dbus_show()
        return True
    except Exception as e:
        log.debug("No running daemon to show: %s", e)
        return False
