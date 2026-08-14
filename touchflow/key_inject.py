"""Ввод клавиш через uinput — работает на X11 и Wayland."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from evdev import UInput

KEY_MAP = {
    "KEY_A": "a", "KEY_B": "b", "KEY_C": "c", "KEY_D": "d", "KEY_E": "e",
    "KEY_F": "f", "KEY_G": "g", "KEY_H": "h", "KEY_I": "i", "KEY_J": "j",
    "KEY_K": "k", "KEY_L": "l", "KEY_M": "m", "KEY_N": "n", "KEY_O": "o",
    "KEY_P": "p", "KEY_Q": "q", "KEY_R": "r", "KEY_S": "s", "KEY_T": "t",
    "KEY_U": "u", "KEY_V": "v", "KEY_W": "w", "KEY_X": "x", "KEY_Y": "y",
    "KEY_Z": "z",
    "KEY_0": "0", "KEY_1": "1", "KEY_2": "2", "KEY_3": "3", "KEY_4": "4",
    "KEY_5": "5", "KEY_6": "6", "KEY_7": "7", "KEY_8": "8", "KEY_9": "9",
    "KEY_SPACE": "space", "KEY_ENTER": "enter", "KEY_TAB": "tab",
    "KEY_BACKSPACE": "backspace", "KEY_DELETE": "delete",
    "KEY_ESC": "esc", "KEY_LEFT": "left", "KEY_RIGHT": "right",
    "KEY_UP": "up", "KEY_DOWN": "down",
    "KEY_HOME": "home", "KEY_END": "end", "KEY_PAGEUP": "pageup", "KEY_PAGEDOWN": "pagedown",
    "KEY_LEFTSHIFT": "leftshift", "KEY_RIGHTSHIFT": "rightshift",
    "KEY_LEFTCTRL": "leftctrl", "KEY_RIGHTCTRL": "rightctrl",
    "KEY_LEFTALT": "leftalt", "KEY_RIGHTALT": "rightalt",
    "KEY_CAPSLOCK": "capslock",
    "KEY_F1": "f1", "KEY_F2": "f2", "KEY_F3": "f3", "KEY_F4": "f4",
    "KEY_F5": "f5", "KEY_F6": "f6", "KEY_F7": "f7", "KEY_F8": "f8",
    "KEY_F9": "f9", "KEY_F10": "f10", "KEY_F11": "f11", "KEY_F12": "f12",
    "KEY_MINUS": "minus", "KEY_EQUAL": "equal",
    "KEY_LEFTBRACE": "leftbrace", "KEY_RIGHTBRACE": "rightbrace",
    "KEY_BACKSLASH": "backslash", "KEY_SEMICOLON": "semicolon",
    "KEY_APOSTROPHE": "apostrophe", "KEY_GRAVE": "grave",
    "KEY_COMMA": "comma", "KEY_DOT": "dot", "KEY_SLASH": "slash",
}

# Русская раскладка — символ -> (keysym name для латиницы + нужен shift/alt)
RU_MAP = {
    "й": ("q",), "ц": ("w",), "у": ("e",), "к": ("r",), "е": ("t",),
    "н": ("y",), "г": ("u",), "ш": ("i",), "щ": ("o",), "з": ("p",),
    "х": ("bracketleft",), "ъ": ("bracketright",),
    "ф": ("a",), "ы": ("s",), "в": ("d",), "а": ("f",), "п": ("g",),
    "р": ("h",), "о": ("j",), "л": ("k",), "д": ("l",), "ж": ("semicolon",),
    "э": ("apostrophe",), "я": ("z",), "ч": ("x",), "с": ("c",), "м": ("v",),
    "и": ("b",), "т": ("n",), "ь": ("m",), "б": ("comma",), "ю": ("period",),
    "ё": ("grave",),
}


class KeyInjector:
    def __init__(self):
        self._ui: UInput | None = None
        self._shift = False
        self._ctrl = False
        self._alt = False
        self._caps = False
        self._layout = "ru"
        self._available = False
        self._init()

    def _init(self) -> None:
        if os.geteuid() != 0 and not os.access("/dev/uinput", os.W_OK):
            # Проверяем группу input
            try:
                import grp

                gid = grp.getgrnam("input").gr_gid
                if gid not in os.getgroups() and os.getgid() != gid:
                    log.warning("No write access to /dev/uinput — add user to 'input' group")
                    return
            except KeyError:
                log.warning("Group 'input' not found")
                return

        try:
            from evdev import UInput, ecodes

            self._ecodes = ecodes
            caps = {ecodes.EV_KEY: list(ecodes.KEY.values())}
            self._ui = UInput(events=caps, name="TouchFlow Virtual Keyboard", bustype=ecodes.BUS_USB)
            self._available = True
            log.info("uinput keyboard ready")
        except Exception as e:
            log.error("uinput init failed: %s", e)

    @property
    def available(self) -> bool:
        return self._available

    def set_layout(self, layout: str) -> None:
        self._layout = layout

    def tap_key(self, key_name: str) -> None:
        if not self._ui:
            return
        ec = self._ecodes
        keycode = getattr(ec, key_name, None)
        if keycode is None:
            keycode = ec.KEY.get(KEY_MAP.get(key_name, key_name), None)
        if keycode is None:
            log.debug("Unknown key: %s", key_name)
            return
        self._ui.write(ec.EV_KEY, keycode, 1)
        self._ui.syn()
        self._ui.write(ec.EV_KEY, keycode, 0)
        self._ui.syn()

    def chord(self, *key_names: str) -> None:
        """Нажать комбинацию клавиш, например Ctrl+C."""
        if not self._ui:
            return
        ec = self._ecodes
        codes: list[int] = []
        for name in key_names:
            code = getattr(ec, name, None)
            if code is None:
                code = ec.KEY.get(KEY_MAP.get(name, name), None)
            if code is not None:
                codes.append(code)
        for code in codes:
            self._ui.write(ec.EV_KEY, code, 1)
            self._ui.syn()
        for code in reversed(codes):
            self._ui.write(ec.EV_KEY, code, 0)
            self._ui.syn()

    def copy(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_C")

    def paste(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_V")

    def cut(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_X")

    def select_all(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_A")

    def undo(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_Z")

    def redo(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_Y")

    def find(self) -> None:
        self.chord("KEY_LEFTCTRL", "KEY_F")

    def type_text(self, char: str) -> None:
        if not self._ui or len(char) != 1:
            return
        ec = self._ecodes
        if char.isupper():
            self._ui.write(ec.EV_KEY, ec.KEY_LEFTSHIFT, 1)
        key_name = char.lower()
        if self._layout == "ru" and char.lower() in RU_MAP:
            # Для русской раскладки система должна быть переключена — отправляем латинский эквивалент
            key_name = RU_MAP[char.lower()][0]
        keycode = ec.KEY.get(key_name)
        if keycode:
            self._ui.write(ec.EV_KEY, keycode, 1)
            self._ui.syn()
            self._ui.write(ec.EV_KEY, keycode, 0)
            self._ui.syn()
        if char.isupper():
            self._ui.write(ec.EV_KEY, ec.KEY_LEFTSHIFT, 0)
            self._ui.syn()

    def toggle_modifier(self, mod: str, active: bool) -> None:
        if not self._ui:
            return
        ec = self._ecodes
        mapping = {
            "shift": (ec.KEY_LEFTSHIFT, "shift"),
            "ctrl": (ec.KEY_LEFTCTRL, "ctrl"),
            "alt": (ec.KEY_LEFTALT, "alt"),
            "caps": (ec.KEY_CAPSLOCK, "caps"),
        }
        if mod not in mapping:
            return
        keycode, attr = mapping[mod]
        setattr(self, f"_{attr}", active)
        self._ui.write(ec.EV_KEY, keycode, 1 if active else 0)
        self._ui.syn()

    def close(self) -> None:
        if self._ui:
            self._ui.close()
            self._ui = None
