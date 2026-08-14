"""Перехват физических кнопок для управления TouchFlow."""

from __future__ import annotations

import logging
import threading
from typing import Callable

log = logging.getLogger(__name__)


class PhysicalButtonListener:
    def __init__(self, bindings: dict[str, list[str]], on_action: Callable[[str], None]):
        self._bindings = bindings
        self._on_action = on_action
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._device_path = bindings.get("grab_device", "")

    def _action_for_key(self, key_name: str) -> str | None:
        for action, keys in self._bindings.items():
            if action == "grab_device":
                continue
            if key_name in keys:
                return action.replace("_", "-").replace("toggle-visibility", "toggle")
        return None

    def start(self) -> bool:
        try:
            from evdev import InputDevice, categorize, ecodes
        except ImportError:
            log.warning("evdev not available for physical bindings")
            return False

        devices = []
        if self._device_path:
            try:
                devices.append(InputDevice(self._device_path))
            except Exception as e:
                log.error("Cannot open %s: %s", self._device_path, e)
                return False
        else:
            from touchflow.external_kb import list_keyboards

            import glob

            for path in sorted(glob.glob("/dev/input/event*")):
                try:
                    dev = InputDevice(path)
                    if ecodes.EV_KEY in dev.capabilities():
                        devices.append(dev)
                except (PermissionError, OSError):
                    continue

        if not devices:
            log.info("No input devices for physical bindings")
            return False

        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, args=(devices,), daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _loop(self, devices) -> None:
        from evdev import categorize, ecodes
        from select import select

        key_map = {v: k for k, v in ecodes.KEY.items()}

        while not self._stop.is_set():
            try:
                r, _, _ = select([d.fd for d in devices], [], [], 0.5)
                for fd in r:
                    dev = next(d for d in devices if d.fd == fd)
                    for event in dev.read():
                        if event.type == ecodes.EV_KEY and event.value == 1:
                            key_name = key_map.get(event.code, "")
                            action = self._action_for_key(key_name)
                            if action:
                                log.debug("Physical key %s -> %s", key_name, action)
                                self._on_action(action)
            except Exception as e:
                if not self._stop.is_set():
                    log.debug("Physical listener: %s", e)
