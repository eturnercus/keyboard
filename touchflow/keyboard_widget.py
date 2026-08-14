"""Виджет экранной клавиатуры с поддержкой мультитача и мультиязычности."""

from __future__ import annotations

import logging
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gtk

from touchflow.config import TouchFlowConfig
from touchflow.gtk_compat import connect_pressed, new_press_gesture
from touchflow.key_inject import KeyInjector
from touchflow.layouts import (
    NUMPAD,
    ROW_ARROWS,
    ROW_NUM,
    ROW_NUMBERS,
    get_language_name,
    get_layout_rows,
)

log = logging.getLogger(__name__)

# Быстрые действия: (подпись, action_id, ширина)
QUICK_ACTIONS = [
    ("Копир.", "ACTION_COPY", 1.3),
    ("Встав.", "ACTION_PASTE", 1.3),
    ("Вырез.", "ACTION_CUT", 1.2),
    ("Всё", "ACTION_SELECT_ALL", 1.0),
    ("Отмена", "ACTION_UNDO", 1.2),
    ("Повт.", "ACTION_REDO", 1.1),
    ("Поиск", "ACTION_FIND", 1.1),
]

ACTION_HANDLERS = {
    "ACTION_COPY": "copy",
    "ACTION_PASTE": "paste",
    "ACTION_CUT": "cut",
    "ACTION_SELECT_ALL": "select_all",
    "ACTION_UNDO": "undo",
    "ACTION_REDO": "redo",
    "ACTION_FIND": "find",
}


class TouchKey(Gtk.Button):
    def __init__(self, label: str, action: str, config: TouchFlowConfig, injector: KeyInjector, on_action: Callable):
        super().__init__()
        self.action = action
        self._config = config
        self._injector = injector
        self._on_action = on_action
        self._shift_active = False

        self.set_label(label)
        self.add_css_class("touchflow-key")
        self.set_hexpand(True)
        self.set_vexpand(True)
        # GTK4: у Gtk.Button нет сигнала "pressed", только "clicked"
        self.connect("clicked", self._on_clicked)

        if config.behavior.multitouch_enabled:
            gesture = new_press_gesture(exclusive=False)
            if gesture is not None:
                connect_pressed(gesture, self._on_gesture_pressed)
                self.add_controller(gesture)

    def _on_clicked(self, *_):
        self._fire()

    def _on_gesture_pressed(self, gesture, n_press, x, y):
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
        if action in ACTION_HANDLERS:
            getattr(self._injector, ACTION_HANDLERS[action])()
            self._on_action("quick_action", action)
            return
        if action.startswith("KEY_"):
            self._injector.tap_key(action)
        else:
            self._injector.type_text(action)
        self._on_action("key_pressed", action)


class KeyboardWidget(Gtk.Box):
    _css_applied = False

    def __init__(self, config: TouchFlowConfig, injector: KeyInjector, on_action: Callable):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=config.layout.key_spacing)
        self._config = config
        self._injector = injector
        self._on_action = on_action
        self._current_lang = config.get_default_language()
        self._injector.set_layout(self._current_lang)
        self._apply_global_css()
        self._build()

    @classmethod
    def _apply_global_css(cls) -> None:
        if cls._css_applied:
            return
        css = """
        button.touchflow-key {
            padding: 4px;
            border: 1px solid #45475a;
        }
        button.touchflow-key:active {
            opacity: 0.85;
        }
        button.touchflow-key.active {
            background-color: #89b4fa;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        cls._css_applied = True

    def _build(self) -> None:
        cfg = self._config
        self.set_spacing(cfg.layout.key_spacing)
        self.add_css_class("touchflow-keyboard")

        c, t, l = cfg.colors, cfg.typography, cfg.layout
        bg_css = f"""
        .touchflow-keyboard {{
            background-color: {c.background};
            padding: {l.key_spacing}px;
        }}
        button.touchflow-key {{
            background-color: {c.key_background};
            color: {c.key_text};
            border-radius: {l.key_radius}px;
            font-family: {t.font_family};
            font-size: {t.font_size}px;
            font-weight: {"bold" if t.bold_labels else "normal"};
            min-height: {l.row_height - l.key_spacing * 2}px;
            border: 1px solid {c.border};
        }}
        button.touchflow-key:active {{
            background-color: {c.key_pressed};
        }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(bg_css.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        if cfg.layout.show_function_row:
            self._add_row(ROW_NUMBERS)
        if cfg.layout.show_number_row:
            self._add_row(ROW_NUM)

        for row in get_layout_rows(self._current_lang):
            self._add_row(row)

        if cfg.layout.show_arrow_row:
            self._add_row(ROW_ARROWS)

        if cfg.layout.show_quick_actions:
            self._add_row(QUICK_ACTIONS)

        self._add_bottom_row()

        if cfg.layout.show_numpad:
            self._add_numpad()

    def _lang_switch_label(self) -> str:
        langs = self._config.languages
        if langs.show_current_lang_on_key:
            return self._current_lang.upper()
        return langs.switch_key_label

    def _add_bottom_row(self) -> None:
        bottom = []
        if self._config.languages.show_switch_key and len(self._config.get_enabled_languages()) > 1:
            bottom.append((self._lang_switch_label(), "SWITCH_LANG", 1.5))
        bottom.extend([
            ("Ctrl", "MOD_CTRL", 1.2), ("Alt", "MOD_ALT", 1.2),
            (" ", "KEY_SPACE", 5), ("◀", "KEY_LEFT", 1), ("▲", "KEY_UP", 1),
            ("▼", "KEY_DOWN", 1), ("▶", "KEY_RIGHT", 1), ("✕", "HIDE", 1.2),
        ])
        self._add_row(bottom)

    def _add_row(self, keys: list) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self._config.layout.key_spacing)
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
                act = action if action.startswith("KEY_") else action
                btn = TouchKey(label, act, self._config, self._injector, self._handle_action)
                grid.attach(btn, c, r, span, 1)
                c += span
        self.append(grid)

    def _handle_action(self, action: str, detail: str = "") -> None:
        if action == "switch_lang":
            self._current_lang = self._config.next_language(self._current_lang)
            self._injector.set_layout(self._current_lang)
            log.info("Language switched to %s (%s)", self._current_lang, get_language_name(self._current_lang))
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
        enabled = config.get_enabled_languages()
        codes = [e.code for e in enabled]
        if self._current_lang not in codes:
            self._current_lang = config.get_default_language()
        self._rebuild()

    @property
    def current_language(self) -> str:
        return self._current_lang
