"""Отслеживание фокуса текстовых полей через AT-SPI (работает в GTK/Qt и др.)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

log = logging.getLogger(__name__)

try:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi, GLib
except (ImportError, ValueError):
    Atspi = None  # type: ignore
    GLib = None  # type: ignore


@dataclass
class FocusInfo:
    app_id: str = ""
    window_class: str = ""
    role: str = ""
    is_text_entry: bool = False
    name: str = ""


TEXT_ROLES = {
    "entry",
    "password text",
    "text",
    "editable text",
    "terminal",
    "document text",
    "spin button",
    "combo box",
}


class FocusWatcher:
    def __init__(self, on_focus_change: Callable[[FocusInfo], None]):
        self._callback = on_focus_change
        self._listener_id: int | None = None
        self._available = Atspi is not None

    @property
    def available(self) -> bool:
        return self._available

    def start(self) -> bool:
        if not self._available:
            log.warning("AT-SPI unavailable — auto-show disabled")
            return False
        try:
            Atspi.init()
            self._listener_id = Atspi.EventListener.register_full(
                self._on_event,
                "object:state-change:focused",
            )
            log.info("AT-SPI focus watcher started")
            return True
        except Exception as e:
            log.error("Failed to start AT-SPI: %s", e)
            self._available = False
            return False

    def stop(self) -> None:
        if self._listener_id is not None and self._available:
            try:
                Atspi.EventListener.deregister(self._listener_id)
            except Exception:
                pass
            self._listener_id = None

    def _on_event(self, event) -> None:
        try:
            info = self._extract_focus(event.source)
            self._callback(info)
        except Exception as e:
            log.debug("Focus event error: %s", e)

    def _extract_focus(self, accessible) -> FocusInfo:
        info = FocusInfo()
        if accessible is None:
            return info

        try:
            role = accessible.get_role_name().lower()
            info.role = role
            info.name = accessible.get_name() or ""
            states = accessible.get_state_set()
            focused = states.contains(Atspi.StateType.FOCUSED)
            editable = states.contains(Atspi.StateType.EDITABLE)
            info.is_text_entry = focused and (role in TEXT_ROLES or editable)
        except Exception:
            pass

        try:
            app = accessible.get_application()
            if app:
                info.app_id = (app.get_name() or "").lower()
        except Exception:
            pass

        try:
            top = accessible
            for _ in range(20):
                parent = top.get_parent()
                if parent is None:
                    break
                top = parent
            info.window_class = (top.get_name() or "").lower()
        except Exception:
            pass

        return info

    def poll_current(self) -> FocusInfo:
        if not self._available:
            return FocusInfo()
        try:
            desktop = Atspi.get_desktop(0)
            focused = desktop.get_child_at_index(0)
            if focused:
                return self._extract_focus(focused)
        except Exception:
            pass
        return FocusInfo()
