"""Полупрозрачное обучение при первом запуске (только один раз)."""

from __future__ import annotations

import logging
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk

from touchflow.config import FIRST_RUN_PATH, ensure_config_dir

log = logging.getLogger(__name__)

STEPS = [
    {
        "title": "Добро пожаловать в TouchFlow!",
        "body": "Экранная клавиатура для сенсорных Linux-устройств.\n\nПроведите краткий тур — это займёт 30 секунд.",
        "icon": "👋",
    },
    {
        "title": "Авто-показ",
        "body": "Клавиатура появляется автоматически при нажатии на поле ввода.\n\nЕсли подключена USB/BT клавиатура — скрывается сама.",
        "icon": "⌨️",
    },
    {
        "title": "Свайп снизу",
        "body": "Проведите пальцем снизу экрана вверх —\nклавиатура появится в любой момент.",
        "icon": "👆",
    },
    {
        "title": "Смена языка",
        "body": "Кнопка 🌐 переключает языки.\n\nРусский, English и другие — настраиваются в TouchFlow Settings.",
        "icon": "🌐",
    },
    {
        "title": "Обучение",
        "body": "TouchFlow запоминает, где вы скрываете клавиатуру,\nи перестаёт показывать её в этих приложениях.\n\nУправляйте этим в Настройки → Обучение.",
        "icon": "🧠",
    },
    {
        "title": "Готово!",
        "body": "Настройки: запустите touchflow-settings\nили найдите «TouchFlow Settings» в меню.\n\nПриятного использования!",
        "icon": "✅",
    },
]


def is_first_run() -> bool:
    return not FIRST_RUN_PATH.exists()


def mark_first_run_complete() -> None:
    ensure_config_dir()
    FIRST_RUN_PATH.write_text("completed\n", encoding="utf-8")
    log.info("First-run onboarding marked complete")


def reset_first_run_flag() -> None:
    if FIRST_RUN_PATH.exists():
        FIRST_RUN_PATH.unlink()


class OnboardingWindow(Gtk.Window):
    """Полупрозрачное окно обучения — показывается только при первом запуске."""

    def __init__(self, on_complete: Callable[[], None] | None = None):
        super().__init__()
        self._on_complete = on_complete
        self._step = 0

        self.set_title("TouchFlow — Добро пожаловать")
        self.set_default_size(520, 380)
        self.set_modal(True)
        self.set_transient_for(None)
        self.set_opacity(0.92)
        self.set_decorated(True)

        css = """
        window {
            background-color: alpha(#1e1e2e, 0.95);
        }
        .onboarding-card {
            background-color: #313244;
            border-radius: 16px;
            padding: 32px;
        }
        .onboarding-icon {
            font-size: 48px;
        }
        .onboarding-title {
            font-size: 22px;
            font-weight: bold;
            color: #cdd6f4;
        }
        .onboarding-body {
            font-size: 14px;
            color: #a6adc8;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.add_css_class("onboarding-card")
        outer.set_margin_top(16)
        outer.set_margin_bottom(16)
        outer.set_margin_start(16)
        outer.set_margin_end(16)

        self._icon = Gtk.Label(label="👋")
        self._icon.add_css_class("onboarding-icon")
        self._icon.set_halign(Gtk.Align.CENTER)
        outer.append(self._icon)

        self._title = Gtk.Label(label="")
        self._title.add_css_class("onboarding-title")
        self._title.set_halign(Gtk.Align.CENTER)
        self._title.set_margin_top(16)
        outer.append(self._title)

        self._body = Gtk.Label(label="")
        self._body.add_css_class("onboarding-body")
        self._body.set_halign(Gtk.Align.CENTER)
        self._body.set_justify(Gtk.Justification.CENTER)
        self._body.set_margin_top(12)
        outer.append(self._body)

        self._dots = Gtk.Label(label="")
        self._dots.add_css_class("dim-label")
        self._dots.set_halign(Gtk.Align.CENTER)
        self._dots.set_margin_top(24)
        outer.append(self._dots)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(24)

        self._skip_btn = Gtk.Button(label="Пропустить")
        self._skip_btn.connect("clicked", self._finish)
        btn_box.append(self._skip_btn)

        self._next_btn = Gtk.Button(label="Далее")
        self._next_btn.add_css_class("suggested-action")
        self._next_btn.connect("clicked", self._next)
        btn_box.append(self._next_btn)

        outer.append(btn_box)
        self.set_child(outer)
        self._render_step()

    def _render_step(self) -> None:
        step = STEPS[self._step]
        self._icon.set_text(step["icon"])
        self._title.set_text(step["title"])
        self._body.set_text(step["body"])
        dots = " ".join("●" if i == self._step else "○" for i in range(len(STEPS)))
        self._dots.set_text(f"{dots}  ({self._step + 1}/{len(STEPS)})")
        if self._step == len(STEPS) - 1:
            self._next_btn.set_label("Начать!")
        else:
            self._next_btn.set_label("Далее")

    def _next(self, *_):
        if self._step < len(STEPS) - 1:
            self._step += 1
            self._render_step()
        else:
            self._finish()

    def _finish(self, *_args):
        mark_first_run_complete()
        self.close()
        if self._on_complete:
            self._on_complete()


def show_onboarding_if_needed(parent: Gtk.Window | None = None, on_complete: Callable | None = None) -> bool:
    """Показать обучение если первый запуск. Возвращает True если показано."""
    if not is_first_run():
        return False
    win = OnboardingWindow(on_complete=on_complete)
    if parent:
        win.set_transient_for(parent)
    win.present()
    return True
