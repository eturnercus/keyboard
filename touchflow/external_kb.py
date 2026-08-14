"""Обнаружение подключённых физических клавиатур."""

from __future__ import annotations

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

INPUT_DEVICES = Path("/proc/bus/input/devices")
KEYBOARD_CAP = re.compile(r"\bEV_KEY\b")


def _parse_devices(text: str) -> list[dict[str, str]]:
    blocks = text.strip().split("\n\n")
    devices: list[dict[str, str]] = []
    for block in blocks:
        info: dict[str, str] = {}
        for line in block.splitlines():
            if line.startswith("I:"):
                m = re.search(r"bus=(\S+)", line, re.IGNORECASE)
                if m:
                    info["bus"] = m.group(1)
            elif line.startswith("N:"):
                info["name"] = line.split("Name=", 1)[-1].strip().strip('"')
            elif line.startswith("H:"):
                info["handlers"] = line.split("Handlers=", 1)[-1].strip()
            elif line.startswith("B:") and "EV_KEY" in line:
                info["has_keys"] = "1"
        if info.get("has_keys"):
            devices.append(info)
    return devices


def list_keyboards() -> list[dict[str, str]]:
    if not INPUT_DEVICES.exists():
        return []
    text = INPUT_DEVICES.read_text(encoding="utf-8", errors="replace")
    return _parse_devices(text)


def _is_keyboard_device(dev: dict[str, str]) -> bool:
    name = dev.get("name", "").lower()
    handlers = dev.get("handlers", "")
    skip_patterns = (
        "touchflow",
        "virtual",
        "uinput",
        "dummy",
        "power button",
        "sleep button",
        "video bus",
        "gpio",
    )
    if any(p in name for p in skip_patterns):
        return False
    return "event" in handlers and "kbd" in handlers


def has_pluggable_keyboard() -> bool:
    """USB / Bluetooth / I2C HID — блокирует авто-показ при hide_on_external_keyboard."""
    for dev in list_keyboards():
        if not _is_keyboard_device(dev):
            continue
        bus = dev.get("bus", "")
        if bus in ("0003", "0005", "0018"):
            log.debug("Pluggable keyboard: %s (%s)", dev.get("name"), bus)
            return True
    return False


def has_builtin_keyboard() -> bool:
    """Встроенная клавиатура ноутбука (i8042) — не блокирует авто-показ."""
    for dev in list_keyboards():
        if not _is_keyboard_device(dev):
            continue
        if dev.get("bus") == "0011":
            log.debug("Built-in keyboard: %s", dev.get("name"))
            return True
    return False


def has_external_keyboard() -> bool:
    """Любая физическая клавиатура (для диагностики)."""
    return has_pluggable_keyboard() or has_builtin_keyboard()


class ExternalKeyboardMonitor:
    """Периодический опрос /proc/bus/input/devices (надёжно на всех дистрибутивах)."""

    def __init__(self, on_change=None):
        self._on_change = on_change
        self._connected = has_pluggable_keyboard()

    @property
    def connected(self) -> bool:
        return self._connected

    def poll(self) -> bool:
        current = has_pluggable_keyboard()
        if current != self._connected:
            self._connected = current
            if self._on_change:
                self._on_change(current)
        return current
