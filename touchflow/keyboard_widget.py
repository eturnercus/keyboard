"""Виджет экранной клавиатуры с поддержкой мультитача."""

from __future__ import annotations

import logging
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from touchflow.config import TouchFlowConfig
from touchflow.key_inject import KeyInjector

log = logging.getLogger(__name__)

# Раскладки клавиш: (label, action, width_factor)
ROW_NUMBERS = [
    ("Esc", "KEY_ESC", 1), ("F1", "KEY_F1", 1), ("F2", "KEY_F2", 1), ("F3", "KEY_F3", 1),
    ("F4", "KEY_F4", 1), ("F5", "KEY_F5", 1), ("F6", "KEY_F6", 1), ("F7", "KEY_F7", 1),
    ("F8", "KEY_F8", 1), ("F9", "KEY_F9", 1), ("F10", "KEY_F10", 1), ("F11", "KEY_F11", 1),
    ("F12", "KEY_F12", 1),
]

ROW_NUM = [
    ("1", "1", 1), ("2", "2", 1), ("3", "3", 1), ("4", "4", 1), ("5", "5", 1),
    ("6", "6", 1), ("7", "7", 1), ("8", "8", 1), ("9", "9", 1), ("0", "0", 1),
    ("-", "KEY_MINUS", 1), ("=", "KEY_EQUAL", 1), ("⌫", "KEY_BACKSPACE", 2),
]

ROW_RU_1 = [
    ("й", "й", 1), ("ц", "ц", 1), ("у", "у", 1), ("к", "к", 1), ("е", "е", 1),
    ("н", "н", 1), ("г", "г", 1), ("ш", "ш", 1), ("щ", "щ", 1), ("з", "з", 1),
    ("х", "х", 1), ("ъ", "ъ", 1), ("\\", "KEY_BACKSLASH", 1),
]

ROW_RU_2 = [
    ("Tab", "KEY_TAB", 1.5), ("ф", "ф", 1), ("ы", "ы", 1), ("в", "в", 1), ("а", "а", 1),
    ("п", "п", 1), ("р", "р", 1), ("о", "о", 1), ("л", "л", 1), ("д", "д", 1),
    ("ж", "ж", 1), ("э", "э", 1), ("Enter", "KEY_ENTER", 1.5),
]

ROW_RU_3 = [
    ("⇧", "MOD_SHIFT", 2), ("я", "я", 1), ("ч", "ч", 1), ("с", "с", 1), ("м", "м", 1),
    ("и", "и", 1), ("т", "т", 1), ("ь", "ь", 1), ("б", "б", 1), ("ю", "ю", 1),
    ("ё", "ё", 1), ("⇧", "MOD_SHIFT", 2),
]

ROW_EN_1 = [
    ("q", "q", 1), ("w", "w", 1), ("e", "e", 1), ("r", "r", 1), ("t", "t", 1),
    ("y", "y", 1), ("u", "u", 1), ("i", "i", 1), ("o", "o", 1), ("p", "p", 1),
    ("[", "KEY_LEFTBRACE", 1), ("]", "KEY_RIGHTBRACE", 1),
]

ROW_EN_2 = [
    ("Tab", "KEY_TAB", 1.5), ("a", "a", 1), ("b", "b", 1), ("c", "c", 1), ("d", "d", 1),
    ("e", "e", 1), ("f", "f", 1), ("g", "g", 1), ("h", "h", 1), ("i", "i", 1),
    ("j", "j", 1), ("k", "k", 1), ("l", "l", 1), (";", "KEY_SEMICOLON", 1),
    ("'", "KEY_APOSTROPHE", 1), ("Enter", "KEY_ENTER", 1.5),
]

ROW_EN_3 = [
    ("⇧", "MOD_SHIFT", 2), ("z", "z", 1), ("x", "x", 1), ("c", "c", 1), ("v", "v", 1),
    ("b", "b", 1), ("n", "n", 1), ("m", "m", 1), (",", "KEY_COMMA", 1), (".", "KEY_DOT", 1),
    ("/", "KEY_SLASH", 1), ("⇧", "MOD_SHIFT", 2),
]

ROW_BOTTOM = [
    ("🌐", "SWITCH_LANG", 1.5), ("Ctrl", "MOD_CTRL", 1.2), ("Alt", "MOD_ALT", 1.2),
    (" ", "KEY_SPACE", 5), ("◀", "KEY_LEFT", 1), ("▲", "KEY_UP", 1),
    ("▼", "KEY_DOWN", 1), ("▶", "KEY_RIGHT", 1), ("✕", "HIDE", 1.2),
]

ROW_ARROWS = [
    ("", "", 8), ("◀", "KEY_LEFT", 1), ("▲", "KEY_UP", 1),
    ("▼", "KEY_DOWN", 1), ("▶", "KEY_RIGHT", 1),
]

NUMPAD = [
    [("7", "7"), ("8", "8"), ("9", "9"), ("/", "KEY_SLASH")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("*", "KEY_KPASTERISK")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("-", "KEY_MINUS")],
    [("0", "0", 2), (".", "KEY_DOT"), ("Enter", "KEY_ENTER")],
]


class TouchKey(Gtk.Button):
    """Кнопка клавиши с поддержкой мультитача через отдельные gesture."""

    def __init__(self, label: str, action: str, config: TouchFlowConfig, injector: KeyInjector, on_action: Callable):
        super().__init__()
        self.action = action
        self._config = config
        self._injector = injector
        self._on_action = on_action
        self._shift_active = False
        self._pressed = False

        self.set_label(label)
        self.add_css_class("touchflow-key")
        self.set_hexpand(True)
        self.set_vexpand(True)

        self._apply_style()
        self.connect("pressed", self._on_pressed)
        self.connect("released", self._on_released)

        if config.behavior.multitouch_enabled:
            gesture = Gtk.GestureMultiPress.new()
            gesture.set_exclusive(False)
            gesture.connect("pressed", self._on_multitouch_pressed)
            self.add_controller(gesture)

    def _apply_style(self) -> None:
        c = self._config.colors
        t = self._config.typography
        l = self._config.layout
        css = f"""
        button.touchflow-key {{
            background-color: {c.key_background};
            color: {c.key_text};
            border-radius: {l.key_radius}px;
            font-family: {t.font_family};
            font-size: {t.font_size}px;
            font-weight: {"bold" if t.bold_labels else "normal"};
            min-height: {l.row_height - l.key_spacing * 2}px;
            padding: 4px;
            border: 1px solid {c.border};
        }}
        button.touchflow-key:active {{
            background-color: {c.key_pressed};
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

    def _on_pressed(self, *_):
        self._pressed = True
        self._fire()

    def _on_released(self, *_):
        self._pressed = False

    def _on_multitouch_pressed(self, gesture, n_press, x, y):
        if n_press == 1:
            self._fire()

    def _fire(self):
        action = self.action
        if action == "MOD_SHIFT":
            self._shift_active = not self._shift_active
            self._injector.toggle_modifier("shift", self._shift_active)
            if self._shift_active:
                self.add_css_class("active")
            else:
                self.remove_css_class("active")
            return
        if action == "MOD_CTRL":
            self._injector.toggle_modifier("ctrl", not self._injector._ctrl)
            return
        if action == "MOD_ALT":
            self._injector.toggle_modifier("alt", not self._injector._alt)
            return
        if action == "SWITCH_LANG":
            self._on_action("switch_lang")
            return
        if action == "HIDE":
            self._on_action("hide")
            return
        if action.startswith("KEY_"):
            self._injector.tap_key(action)
        else:
            self._injector.type_text(action)
        self._on_action("key_pressed", action)


class KeyboardWidget(Gtk.Box):
    def __init__(self, config: TouchFlowConfig, injector: KeyInjector, on_action: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=config.layout.key_spacing)
        self._config = config
        self._injector = injector
        self._on_action = on_action
        self._layout = config.locale.primary
        self._shift = False
        self._build()

    def _build(self) -> None:
        cfg = self._config
        self.set_spacing(cfg.layout.key_spacing)
        self.add_css_class("touchflow-keyboard")

        bg_css = f"""
        .touchflow-keyboard {{
            background-color: {cfg.colors.background};
            padding: {cfg.layout.key_spacing}px;
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(bg_css.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        if cfg.layout.show_function_row:
            self._add_row(ROW_NUMBERS)

        if cfg.layout.show_number_row:
            self._add_row(ROW_NUM)

        if self._layout == "ru":
            self._add_row(ROW_RU_1)
            self._add_row(ROW_RU_2)
            self._add_row(ROW_RU_3)
        else:
            self._add_row(ROW_EN_1)
            self._add_row(ROW_EN_2)
            self._add_row(ROW_EN_3)

        if cfg.layout.show_arrow_row:
            self._add_row(ROW_ARROWS)

        self._add_row(ROW_BOTTOM)

        if cfg.layout.show_numpad:
            self._add_numpad()

    def _add_row(self, keys: list) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self._config.layout.key_spacing)
        row.set_homogeneous(False)
        for item in keys:
            label, action = item[0], item[1]
            width = item[2] if len(item) > 2 else 1
            if not label and action == "":
                spacer = Gtk.Box()
                spacer.set_hexpand(True)
                row.append(spacer)
                continue
            btn = TouchKey(label, action, self._config, self._injector, self._handle_action)
            if width > 1:
                btn.set_size_request(int(40 * width), -1)
            row.append(btn)
        self.append(row)

    def _add_numpad(self) -> None:
        grid = Gtk.Grid(column_spacing=4, row_spacing=4)
        for r, nrow in enumerate(NUMPAD):
            c = 0
            for item in nrow:
                label, action = item[0], item[1]
                span = item[2] if len(item) > 2 else 1
                btn = TouchKey(label, action if action.startswith("KEY_") else action, self._config, self._injector, self._handle_action)
                grid.attach(btn, c, r, span, 1)
                c += span
        self.append(grid)

    def _handle_action(self, action: str, detail: str = "") -> None:
        if action == "switch_lang":
            self._layout = "en" if self._layout == "ru" else "ru"
            self._injector.set_layout(self._layout)
            self._rebuild()
        self._on_action(action, detail)

    def _rebuild(self) -> None:
        child = self.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.remove(child)
            child = next_child
        self._build()

    def apply_config(self, config: TouchFlowConfig) -> None:
        self._config = config
        self._rebuild()
