"""TouchFlow Settings — отдельное приложение настройки."""

from __future__ import annotations

import logging
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gtk

from touchflow import SETTINGS_ID, __version__
from touchflow.config import TouchFlowConfig, load_config, reset_config, save_config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("touchflow-settings")


class ColorRow(Gtk.Box):
    def __init__(self, label: str, color: str, on_change):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._on_change = on_change
        lbl = Gtk.Label(label=label)
        lbl.set_hexpand(True)
        lbl.set_xalign(0)
        self.append(lbl)
        btn = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(color)
        btn.set_rgba(rgba)
        btn.connect("color-set", self._changed)
        self.append(btn)

    def _changed(self, btn):
        rgba = btn.get_rgba()
        self._on_change(rgba.to_string())


class SpinRow(Gtk.Box):
    def __init__(self, label: str, value: int, min_v: int, max_v: int, on_change):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._on_change = on_change
        lbl = Gtk.Label(label=label)
        lbl.set_hexpand(True)
        lbl.set_xalign(0)
        self.append(lbl)
        spin = Gtk.SpinButton.new_with_range(min_v, max_v, 1)
        spin.set_value(value)
        spin.connect("value-changed", lambda s: on_change(int(s.get_value())))
        self.append(spin)


class SwitchRow(Gtk.Box):
    def __init__(self, label: str, subtitle: str, active: bool, on_change):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title = Gtk.Label(label=label, xalign=0)
        title.add_css_class("title-4")
        box.append(title)
        if subtitle:
            sub = Gtk.Label(label=subtitle, xalign=0)
            sub.add_css_class("dim-label")
            box.append(sub)
        box.set_hexpand(True)
        self.append(box)
        sw = Gtk.Switch(active=active)
        sw.connect("notify::active", lambda s, _: on_change(s.get_active()))
        self.append(sw)


class SettingsPage(Gtk.Box):
    def __init__(self, app: "SettingsApp"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._app = app

    def build(self) -> Gtk.Widget:
        raise NotImplementedError


class BehaviorPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        cfg = self._app.config
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        rows = [
            ("Авто-показ при фокусе", "Показывать клавиатуру при нажатии на поле ввода", cfg.behavior.auto_show,
             lambda v: self._set("behavior", "auto_show", v)),
            ("Авто-скрытие", "Скрывать при потере фокуса", cfg.behavior.auto_hide_on_blur,
             lambda v: self._set("behavior", "auto_hide_on_blur", v)),
            ("Скрывать при внешней клавиатуре", "Не показывать если подключена USB/BT клавиатура", cfg.behavior.hide_on_external_keyboard,
             lambda v: self._set("behavior", "hide_on_external_keyboard", v)),
            ("Показ при отключении клавиатуры", "Авто-показ когда внешняя клавиатура отключена", cfg.behavior.show_on_external_keyboard_disconnect,
             lambda v: self._set("behavior", "show_on_external_keyboard_disconnect", v)),
            ("Свайп снизу", "Проведите пальцем снизу вверх для показа", cfg.behavior.swipe_from_bottom,
             lambda v: self._set("behavior", "swipe_from_bottom", v)),
            ("Обучение", "Запоминать когда показывать и когда скрывать", cfg.behavior.learning_enabled,
             lambda v: self._set("behavior", "learning_enabled", v)),
            ("Мультитач", "Несколько клавиш одновременно", cfg.behavior.multitouch_enabled,
             lambda v: self._set("behavior", "multitouch_enabled", v)),
        ]
        for title, sub, active, cb in rows:
            box.append(SwitchRow(title, sub, active, cb))

        box.append(SpinRow("Высота зоны свайпа (px)", cfg.behavior.swipe_zone_height_px, 8, 80,
                           lambda v: self._set("behavior", "swipe_zone_height_px", v)))
        box.append(SpinRow("Порог свайпа (px)", cfg.behavior.swipe_threshold_px, 30, 300,
                           lambda v: self._set("behavior", "swipe_threshold_px", v)))
        box.append(SpinRow("Анимация (мс)", cfg.behavior.animation_ms, 0, 1000,
                           lambda v: self._set("behavior", "animation_ms", v)))

        clamp.set_child(box)
        return clamp

    def _set(self, section, key, value):
        setattr(getattr(self._app.config, section), key, value)
        self._app.mark_dirty()


class LayoutPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        cfg = self._app.config
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        box.append(SpinRow("Высота клавиатуры (px)", cfg.layout.height_px, 150, 600,
                           lambda v: self._set("height_px", v)))
        box.append(SpinRow("Ширина (%)", cfg.layout.width_percent, 50, 100,
                           lambda v: self._set("width_percent", v)))
        box.append(SpinRow("Высота ряда (px)", cfg.layout.row_height, 32, 100,
                           lambda v: self._set("row_height", v)))
        box.append(SpinRow("Отступ клавиш (px)", cfg.layout.key_spacing, 0, 20,
                           lambda v: self._set("key_spacing", v)))
        box.append(SpinRow("Скругление (px)", cfg.layout.key_radius, 0, 24,
                           lambda v: self._set("key_radius", v)))

        for title, key, val in [
            ("Ряд F1–F12", "show_function_row", cfg.layout.show_function_row),
            ("Цифровой ряд", "show_number_row", cfg.layout.show_number_row),
            ("Стрелки", "show_arrow_row", cfg.layout.show_arrow_row),
            ("Numpad", "show_numpad", cfg.layout.show_numpad),
            ("Компактный режим", "compact_mode", cfg.layout.compact_mode),
        ]:
            box.append(SwitchRow(title, "", val, lambda v, k=key: self._set(k, v)))

        clamp.set_child(box)
        return clamp

    def _set(self, key, value):
        setattr(self._app.config.layout, key, value)
        self._app.mark_dirty()


class ColorsPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        cfg = self._app.config
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        for label, key in [
            ("Фон", "background"), ("Клавиши", "key_background"), ("Нажатие", "key_pressed"),
            ("Текст", "key_text"), ("Акцент", "accent"), ("Рамка", "border"),
        ]:
            box.append(ColorRow(label, getattr(cfg.colors, key),
                                lambda c, k=key: self._set_color(k, c)))

        clamp.set_child(box)
        return clamp

    def _set_color(self, key, value):
        setattr(self._app.config.colors, key, value)
        self._app.mark_dirty()


class OverlayPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        cfg = self._app.config
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        box.append(SwitchRow("Включить оверлей", "Полупрозрачные кнопки и джойстик на экране", cfg.overlay.enabled,
                             lambda v: self._set("enabled", v)))
        box.append(SwitchRow("Джойстик", "", cfg.overlay.joystick_enabled,
                             lambda v: self._set("joystick_enabled", v)))
        box.append(SpinRow("Размер джойстика", cfg.overlay.joystick_size_px, 60, 300,
                           lambda v: self._set("joystick_size_px", v)))

        edit_btn = Gtk.Button(label="Режим редактирования оверлея")
        edit_btn.add_css_class("suggested-action")
        edit_btn.connect("clicked", self._toggle_edit)
        box.append(edit_btn)

        info = Gtk.Label(label="Перетаскивайте кнопки в режиме редактирования.\nНастройте действия в config.toml → [overlay.buttons]")
        info.add_css_class("dim-label")
        box.append(info)

        clamp.set_child(box)
        return clamp

    def _set(self, key, value):
        setattr(self._app.config.overlay, key, value)
        self._app.mark_dirty()

    def _toggle_edit(self, *_):
        try:
            from pydbus import SessionBus
            bus = SessionBus()
            proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
            proxy.SetOverlayEditMode(True)
        except Exception as e:
            log.warning("Cannot enable edit mode: %s", e)


class GreeterPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        cfg = self._app.config
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        box.append(SwitchRow("Работа до входа", "Клавиатура на экране входа (GDM/LightDM/SDDM)", cfg.greeter.enabled,
                             lambda v: self._set("enabled", v)))

        info = Gtk.Label(
            label="После установки выполните:\nsudo ./scripts/install-greeter.sh\n\nЭто настроит systemd-сервис для дисплей-менеджера.",
            xalign=0,
        )
        info.add_css_class("dim-label")
        box.append(info)

        clamp.set_child(box)
        return clamp

    def _set(self, key, value):
        setattr(self._app.config.greeter, key, value)
        self._app.mark_dirty()


class AboutPage(SettingsPage):
    def build(self) -> Gtk.Widget:
        clamp = Adw.Clamp()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(48)
        box.set_halign(Gtk.Align.CENTER)

        title = Gtk.Label(label="TouchFlow Keyboard")
        title.add_css_class("title-1")
        box.append(title)
        ver = Gtk.Label(label=f"Версия {__version__}")
        ver.add_css_class("dim-label")
        box.append(ver)
        desc = Gtk.Label(
            label="Надёжная экранная клавиатура для Linux\nс мультитачем, обучением и глубокой кастомизацией",
            justify=Gtk.Justification.CENTER,
        )
        box.append(desc)

        reset_btn = Gtk.Button(label="Сбросить обучение")
        reset_btn.connect("clicked", self._reset_learning)
        box.append(reset_btn)

        reset_cfg = Gtk.Button(label="Сбросить все настройки")
        reset_cfg.add_css_class("destructive-action")
        reset_cfg.connect("clicked", self._reset_config)
        box.append(reset_cfg)

        clamp.set_child(box)
        return clamp

    def _reset_learning(self, *_):
        try:
            from pydbus import SessionBus
            bus = SessionBus()
            proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
            proxy.ResetLearning()
        except Exception:
            pass

    def _reset_config(self, *_):
        self._app.config = reset_config()
        self._app.mark_dirty()
        self._app.rebuild_pages()


class SettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=SETTINGS_ID)
        self.config = load_config()
        self._dirty = False
        self._stack: Adw.ViewStack | None = None

    def do_activate(self):
        win = Adw.ApplicationWindow(application=self)
        win.set_title("TouchFlow — Настройки")
        win.set_default_size(900, 640)

        header = Adw.HeaderBar()
        save_btn = Gtk.Button(label="Сохранить")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._save)
        header.pack_end(save_btn)
        apply_btn = Gtk.Button(label="Применить")
        apply_btn.connect("clicked", self._apply)
        header.pack_end(apply_btn)

        self._stack = Adw.ViewStack()
        pages = [
            ("Поведение", "behavior-symbolic", BehaviorPage(self)),
            ("Раскладка", "keyboard-symbolic", LayoutPage(self)),
            ("Цвета", "color-select-symbolic", ColorsPage(self)),
            ("Оверлей", "applications-games-symbolic", OverlayPage(self)),
            ("Экран входа", "system-lock-screen-symbolic", GreeterPage(self)),
            ("О программе", "help-about-symbolic", AboutPage(self)),
        ]
        for title, icon, page in pages:
            self._stack.add_titled(page.build(), title, title)

        sidebar = Adw.ViewSwitcher()
        sidebar.set_stack(self._stack)
        sidebar.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self._stack)

        content = Adw.ToolbarView()
        content.add_top_bar(header)
        content.set_content(self._stack)
        content.add_bottom_bar(switcher_bar)

        win.set_content(content)
        win.present()

    def mark_dirty(self):
        self._dirty = True

    def _save(self, *_):
        save_config(self.config)
        self._dirty = False
        self._apply()

    def _apply(self, *_):
        save_config(self.config)
        try:
            from pydbus import SessionBus
            bus = SessionBus()
            proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
            proxy.ReloadConfig()
        except Exception:
            pass

    def rebuild_pages(self):
        pass


def main() -> None:
    app = SettingsApp()
    sys.exit(app.run(sys.argv))
