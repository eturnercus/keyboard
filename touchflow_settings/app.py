"""TouchFlow Settings — полное приложение настройки."""

from __future__ import annotations

import logging
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from touchflow import SETTINGS_ID, __version__
from touchflow.config import (
    AppLearningRule,
    LanguageEntry,
    TouchFlowConfig,
    factory_reset,
    load_config,
    save_config,
)
from touchflow.layouts import available_languages
from touchflow.onboarding import reset_first_run_flag, show_onboarding_if_needed
from touchflow_settings.widgets import (
    ColorRow,
    EntryRow,
    FloatSpinRow,
    SpinRow,
    SwitchRow,
    page_box,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("touchflow-settings")


class SettingsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=SETTINGS_ID)
        self.config = load_config()
        self._dirty = False
        self._win: Adw.ApplicationWindow | None = None
        self._stack: Adw.ViewStack | None = None

    def do_activate(self):
        self._win = Adw.ApplicationWindow(application=self)
        self._win.set_title("TouchFlow — Настройки")
        self._win.set_default_size(960, 680)

        header = Adw.HeaderBar()
        save_btn = Gtk.Button(label="Сохранить")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._save)
        header.pack_end(save_btn)
        apply_btn = Gtk.Button(label="Применить")
        apply_btn.connect("clicked", self._apply)
        header.pack_end(apply_btn)

        self._stack = Adw.ViewStack()
        builders = [
            ("Поведение", self._build_behavior),
            ("Языки", self._build_languages),
            ("Обучение", self._build_learning),
            ("Раскладка", self._build_layout),
            ("Шрифты", self._build_typography),
            ("Цвета", self._build_colors),
            ("Оверлей", self._build_overlay),
            ("Кнопки", self._build_bindings),
            ("Экран входа", self._build_greeter),
            ("О программе", self._build_about),
        ]
        for title, builder in builders:
            clamp = Adw.Clamp()
            clamp.set_child(builder())
            self._stack.add_titled(clamp, title, title)

        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self._stack)

        content = Adw.ToolbarView()
        content.add_top_bar(header)
        content.set_content(self._stack)
        content.add_bottom_bar(switcher_bar)
        self._win.set_content(content)
        self._win.present()

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

    def _build_behavior(self) -> Gtk.Widget:
        cfg = self._app_cfg = self.config
        b = page_box()
        rows = [
            ("Авто-показ при фокусе", "Показывать при нажатии на поле ввода", cfg.behavior.auto_show,
             lambda v: setattr(cfg.behavior, "auto_show", v)),
            ("Авто-скрытие", "Скрывать при потере фокуса", cfg.behavior.auto_hide_on_blur,
             lambda v: setattr(cfg.behavior, "auto_hide_on_blur", v)),
            ("Скрывать при внешней клавиатуре", "Не показывать если USB/BT клавиатура подключена",
             cfg.behavior.hide_on_external_keyboard,
             lambda v: setattr(cfg.behavior, "hide_on_external_keyboard", v)),
            ("Показ при отключении клавиатуры", "Авто-показ когда внешняя клавиатура отключена",
             cfg.behavior.show_on_external_keyboard_disconnect,
             lambda v: setattr(cfg.behavior, "show_on_external_keyboard_disconnect", v)),
            ("Свайп снизу", "Проведите пальцем снизу вверх", cfg.behavior.swipe_from_bottom,
             lambda v: setattr(cfg.behavior, "swipe_from_bottom", v)),
            ("Мультитач", "Несколько клавиш одновременно", cfg.behavior.multitouch_enabled,
             lambda v: setattr(cfg.behavior, "multitouch_enabled", v)),
            ("Долгое нажатие = повтор", "Повтор символа при удержании", cfg.behavior.long_press_repeat,
             lambda v: setattr(cfg.behavior, "long_press_repeat", v)),
            ("Звук нажатия", "Клик при нажатии клавиши", cfg.behavior.click_sound,
             lambda v: setattr(cfg.behavior, "click_sound", v)),
            ("Скрыт при запуске", "Не показывать клавиатуру при старте", cfg.behavior.startup_hidden,
             lambda v: setattr(cfg.behavior, "startup_hidden", v)),
            ("Прикрепить к низу", "Dock внизу экрана", cfg.behavior.dock_bottom,
             lambda v: setattr(cfg.behavior, "dock_bottom", v)),
        ]
        for title, sub, active, cb in rows:
            b.append(SwitchRow(title, sub, active, lambda v, c=cb: (c(v), self.mark_dirty())))

        b.append(SpinRow("Высота зоны свайпа (px)", cfg.behavior.swipe_zone_height_px, 8, 80,
                         lambda v: (setattr(cfg.behavior, "swipe_zone_height_px", v), self.mark_dirty())))
        b.append(SpinRow("Порог свайпа (px)", cfg.behavior.swipe_threshold_px, 30, 300,
                         lambda v: (setattr(cfg.behavior, "swipe_threshold_px", v), self.mark_dirty())))
        b.append(SpinRow("Анимация (мс)", cfg.behavior.animation_ms, 0, 1000,
                         lambda v: (setattr(cfg.behavior, "animation_ms", v), self.mark_dirty())))
        b.append(SpinRow("Макс. одновременных клавиш", cfg.behavior.max_simultaneous_keys, 1, 10,
                         lambda v: (setattr(cfg.behavior, "max_simultaneous_keys", v), self.mark_dirty())))
        return b

    def _build_languages(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()

        b.append(SwitchRow("Кнопка смены языка", "Показывать 🌐 на клавиатуре", cfg.languages.show_switch_key,
                           lambda v: (setattr(cfg.languages, "show_switch_key", v), self.mark_dirty())))
        b.append(SwitchRow("Код языка на кнопке", "RU / EN вместо 🌐", cfg.languages.show_current_lang_on_key,
                           lambda v: (setattr(cfg.languages, "show_current_lang_on_key", v), self.mark_dirty())))

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        b.append(sep)

        title = Gtk.Label(label="Активные языки", xalign=0)
        title.add_css_class("title-3")
        b.append(title)

        avail = available_languages()
        enabled_codes = {e.code for e in cfg.languages.entries if e.enabled}

        for code, name in sorted(avail.items(), key=lambda x: x[1]):
            is_on = code in enabled_codes
            is_default = any(e.code == code and e.is_default for e in cfg.languages.entries)

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            sw = Gtk.Switch(active=is_on)
            sw.connect("notify::active", lambda s, _, c=code, n=name: self._toggle_language(c, n, s.get_active()))
            row.append(sw)
            lbl = Gtk.Label(label=f"{name} ({code.upper()})", xalign=0)
            lbl.set_hexpand(True)
            row.append(lbl)
            if is_default:
                badge = Gtk.Label(label="по умолчанию")
                badge.add_css_class("accent")
                row.append(badge)
            else:
                def_btn = Gtk.Button(label="По умолчанию")
                def_btn.set_sensitive(is_on)
                def_btn.connect("clicked", lambda *_ , c=code: self._set_default_language(c))
                row.append(def_btn)
            b.append(row)

        info = Gtk.Label(
            label="Доступные: Русский, English, Українська, Deutsch, Français.\nДобавить свой язык можно в config.toml → [languages.entries]",
            xalign=0,
        )
        info.add_css_class("dim-label")
        info.set_margin_top(16)
        b.append(info)
        return b

    def _toggle_language(self, code: str, name: str, enabled: bool):
        entries = self.config.languages.entries
        found = False
        for e in entries:
            if e.code == code:
                e.enabled = enabled
                found = True
                break
        if not found and enabled:
            entries.append(LanguageEntry(code, name, True, False))
        if enabled and not any(e.is_default for e in entries if e.enabled):
            for e in entries:
                if e.code == code:
                    e.is_default = True
        if not enabled:
            for e in entries:
                if e.code == code:
                    e.is_default = False
            enabled_list = [e for e in entries if e.enabled]
            if enabled_list and not any(e.is_default for e in enabled_list):
                enabled_list[0].is_default = True
        self.mark_dirty()

    def _set_default_language(self, code: str):
        for e in self.config.languages.entries:
            e.is_default = e.code == code
        self.mark_dirty()
        self._rebuild_stack()

    def _build_learning(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()

        b.append(SwitchRow("Обучение включено", "Автоматически запоминать привычки", cfg.learning.enabled,
                           lambda v: (setattr(cfg.learning, "enabled", v), self.mark_dirty())))
        b.append(FloatSpinRow("Порог показа", "Ниже = реже показывать (0.0–1.0)", cfg.learning.threshold,
                              0.0, 1.0, lambda v: (setattr(cfg.learning, "threshold", v), self.mark_dirty())))
        b.append(FloatSpinRow("Вес скрытия", "Насколько сильно учитывать скрытие", cfg.learning.dismiss_weight,
                              0.1, 3.0, lambda v: (setattr(cfg.learning, "dismiss_weight", v), self.mark_dirty())))
        b.append(FloatSpinRow("Вес показа", "Насколько сильно учитывать показ", cfg.learning.show_weight,
                              0.1, 3.0, lambda v: (setattr(cfg.learning, "show_weight", v), self.mark_dirty())))

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        b.append(sep)

        title = Gtk.Label(label="Правила для приложений", xalign=0)
        title.add_css_class("title-3")
        b.append(title)

        rules_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for rule in cfg.learning.rules:
            rules_box.append(self._learning_rule_row(rule))
        b.append(rules_box)
        self._rules_box = rules_box

        add_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._rule_app = Gtk.Entry(placeholder_text="app_id (firefox, gedit...)")
        self._rule_app.set_hexpand(True)
        add_row.append(self._rule_app)
        self._rule_mode = Gtk.DropDown.new_from_strings(["auto", "always_show", "always_hide"])
        add_row.append(self._rule_mode)
        add_btn = Gtk.Button(label="Добавить правило")
        add_btn.connect("clicked", self._add_learning_rule)
        add_row.append(add_btn)
        b.append(add_row)

        try:
            from touchflow.learning import LearningEngine
            engine = LearningEngine(config=cfg.learning)
            patterns = engine.get_all_patterns()[:20]
            if patterns:
                sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                b.append(sep2)
                hist_title = Gtk.Label(label="История обучения (последние приложения)", xalign=0)
                hist_title.add_css_class("title-4")
                b.append(hist_title)
                for p in patterns:
                    score_lbl = Gtk.Label(
                        label=f"{p.app_id or '?'} | {p.window_class or '?'} — score: {p.score:.2f} (показов: {p.show_count}, скрытий: {p.dismiss_count})",
                        xalign=0,
                    )
                    score_lbl.add_css_class("dim-label")
                    b.append(score_lbl)
        except Exception:
            pass

        reset_btn = Gtk.Button(label="Сбросить обучение")
        reset_btn.connect("clicked", self._reset_learning)
        b.append(reset_btn)
        return b

    def _learning_rule_row(self, rule: AppLearningRule) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl = Gtk.Label(label=f"{rule.app_id} → {rule.mode}", xalign=0)
        lbl.set_hexpand(True)
        row.append(lbl)
        del_btn = Gtk.Button(icon_name="user-trash-symbolic")
        del_btn.add_css_class("destructive-action")
        del_btn.connect("clicked", lambda *_: self._remove_rule(rule))
        row.append(del_btn)
        return row

    def _add_learning_rule(self, *_):
        app_id = self._rule_app.get_text().strip()
        if not app_id:
            return
        mode = self._rule_mode.get_selected()
        modes = ["auto", "always_show", "always_hide"]
        rule = AppLearningRule(app_id=app_id, window_class="", mode=modes[mode])
        self.config.learning.rules.append(rule)
        self._rules_box.append(self._learning_rule_row(rule))
        self._rule_app.set_text("")
        self.mark_dirty()

    def _remove_rule(self, rule: AppLearningRule):
        if rule in self.config.learning.rules:
            self.config.learning.rules.remove(rule)
        self.mark_dirty()
        self._rebuild_stack()

    def _reset_learning(self, *_):
        try:
            from pydbus import SessionBus
            bus = SessionBus()
            proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
            proxy.ResetLearning()
        except Exception:
            from touchflow.learning import LearningEngine
            LearningEngine(config=self.config.learning).reset()
        self._rebuild_stack()

    def _build_layout(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        b.append(SpinRow("Высота клавиатуры (px)", cfg.layout.height_px, 150, 600,
                         lambda v: (setattr(cfg.layout, "height_px", v), self.mark_dirty())))
        b.append(SpinRow("Ширина (%)", cfg.layout.width_percent, 50, 100,
                         lambda v: (setattr(cfg.layout, "width_percent", v), self.mark_dirty())))
        b.append(SpinRow("Высота ряда (px)", cfg.layout.row_height, 32, 100,
                         lambda v: (setattr(cfg.layout, "row_height", v), self.mark_dirty())))
        b.append(SpinRow("Отступ клавиш (px)", cfg.layout.key_spacing, 0, 20,
                         lambda v: (setattr(cfg.layout, "key_spacing", v), self.mark_dirty())))
        b.append(SpinRow("Скругление (px)", cfg.layout.key_radius, 0, 24,
                         lambda v: (setattr(cfg.layout, "key_radius", v), self.mark_dirty())))
        for title, key, val in [
            ("Ряд F1–F12", "show_function_row", cfg.layout.show_function_row),
            ("Цифровой ряд", "show_number_row", cfg.layout.show_number_row),
            ("Стрелки", "show_arrow_row", cfg.layout.show_arrow_row),
            ("Numpad", "show_numpad", cfg.layout.show_numpad),
            ("Быстрые кнопки", "show_quick_actions", cfg.layout.show_quick_actions),
            ("Компактный режим", "compact_mode", cfg.layout.compact_mode),
        ]:
            b.append(SwitchRow(title, "", val,
                               lambda v, k=key: (setattr(cfg.layout, k, v), self.mark_dirty())))
        return b

    def _build_typography(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        b.append(EntryRow("Шрифт", cfg.typography.font_family,
                          lambda v: (setattr(cfg.typography, "font_family", v), self.mark_dirty())))
        b.append(SpinRow("Размер шрифта", cfg.typography.font_size, 8, 32,
                         lambda v: (setattr(cfg.typography, "font_size", v), self.mark_dirty())))
        b.append(SpinRow("Размер подписей", cfg.typography.label_size, 8, 24,
                         lambda v: (setattr(cfg.typography, "label_size", v), self.mark_dirty())))
        b.append(SwitchRow("Жирные подписи", "", cfg.typography.bold_labels,
                           lambda v: (setattr(cfg.typography, "bold_labels", v), self.mark_dirty())))
        return b

    def _build_colors(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        for label, key in [
            ("Фон", "background"), ("Клавиши", "key_background"), ("Нажатие", "key_pressed"),
            ("Текст", "key_text"), ("Акцент", "accent"), ("Рамка", "border"),
        ]:
            b.append(ColorRow(label, getattr(cfg.colors, key),
                              lambda c, k=key: (setattr(cfg.colors, k, c), self.mark_dirty())))
        return b

    def _build_overlay(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        b.append(SwitchRow("Включить оверлей", "Полупрозрачные кнопки и джойстик", cfg.overlay.enabled,
                           lambda v: (setattr(cfg.overlay, "enabled", v), self.mark_dirty())))
        b.append(SwitchRow("Джойстик", "", cfg.overlay.joystick_enabled,
                           lambda v: (setattr(cfg.overlay, "joystick_enabled", v), self.mark_dirty())))
        b.append(SpinRow("Размер джойстика", cfg.overlay.joystick_size_px, 60, 300,
                         lambda v: (setattr(cfg.overlay, "joystick_size_px", v), self.mark_dirty())))
        b.append(FloatSpinRow("Прозрачность", "", cfg.overlay.opacity, 0.1, 1.0,
                              lambda v: (setattr(cfg.overlay, "opacity", v), self.mark_dirty())))
        edit_btn = Gtk.Button(label="Режим редактирования оверлея")
        edit_btn.add_css_class("suggested-action")
        edit_btn.connect("clicked", self._toggle_overlay_edit)
        b.append(edit_btn)
        return b

    def _toggle_overlay_edit(self, *_):
        try:
            from pydbus import SessionBus
            bus = SessionBus()
            proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
            proxy.SetOverlayEditMode(True)
        except Exception as e:
            log.warning("Cannot enable edit mode: %s", e)

    def _build_bindings(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        b.append(EntryRow("Показать/скрыть (клавиши)", ", ".join(cfg.bindings.toggle_visibility),
                          lambda v: (setattr(cfg.bindings, "toggle_visibility", [x.strip() for x in v.split(",") if x.strip()]), self.mark_dirty()),
                          "KEY_F23, KEY_F24"))
        b.append(EntryRow("Показать", ", ".join(cfg.bindings.show_keyboard),
                          lambda v: (setattr(cfg.bindings, "show_keyboard", [x.strip() for x in v.split(",") if x.strip()]), self.mark_dirty())))
        b.append(EntryRow("Скрыть", ", ".join(cfg.bindings.hide_keyboard),
                          lambda v: (setattr(cfg.bindings, "hide_keyboard", [x.strip() for x in v.split(",") if x.strip()]), self.mark_dirty())))
        b.append(EntryRow("Смена языка", ", ".join(cfg.bindings.switch_layout),
                          lambda v: (setattr(cfg.bindings, "switch_layout", [x.strip() for x in v.split(",") if x.strip()]), self.mark_dirty())))
        b.append(EntryRow("Оверлей", ", ".join(cfg.bindings.toggle_overlay),
                          lambda v: (setattr(cfg.bindings, "toggle_overlay", [x.strip() for x in v.split(",") if x.strip()]), self.mark_dirty())))
        b.append(EntryRow("Устройство evdev", cfg.bindings.grab_device,
                          lambda v: (setattr(cfg.bindings, "grab_device", v), self.mark_dirty()),
                          "/dev/input/event0"))
        info = Gtk.Label(label="Формат: KEY_F23, KEY_PROG1 и т.д. (evdev key names)", xalign=0)
        info.add_css_class("dim-label")
        b.append(info)
        return b

    def _build_greeter(self) -> Gtk.Widget:
        cfg = self.config
        b = page_box()
        b.append(SwitchRow("Работа до входа", "GDM / LightDM / SDDM", cfg.greeter.enabled,
                           lambda v: (setattr(cfg.greeter, "enabled", v), self.mark_dirty())))
        info = Gtk.Label(label="sudo ./scripts/install-greeter.sh", xalign=0)
        info.add_css_class("dim-label")
        b.append(info)
        return b

    def _build_about(self) -> Gtk.Widget:
        b = page_box()
        title = Gtk.Label(label="TouchFlow Keyboard")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.CENTER)
        b.append(title)
        b.append(Gtk.Label(label=f"Версия {__version__}", css_classes=["dim-label"]))

        tour_btn = Gtk.Button(label="Показать обучение снова")
        tour_btn.connect("clicked", self._show_onboarding)
        b.append(tour_btn)

        reset_learn = Gtk.Button(label="Сбросить обучение")
        reset_learn.connect("clicked", self._reset_learning)
        b.append(reset_learn)

        reset_cfg = Gtk.Button(label="Сбросить настройки")
        reset_cfg.connect("clicked", self._reset_config)
        b.append(reset_cfg)

        factory = Gtk.Button(label="Полный сброс (заводские настройки)")
        factory.add_css_class("destructive-action")
        factory.connect("clicked", self._factory_reset)
        b.append(factory)
        return b

    def _show_onboarding(self, *_):
        reset_first_run_flag()
        show_onboarding_if_needed(self._win)

    def _reset_config(self, *_):
        from touchflow.config import reset_config
        self.config = reset_config()
        self.mark_dirty()
        self._rebuild_stack()

    def _factory_reset(self, *_):
        self.config = factory_reset()
        self.mark_dirty()
        self._rebuild_stack()

    def _rebuild_stack(self):
        if not self._stack:
            return
        while self._stack.get_first_child():
            self._stack.remove(self._stack.get_first_child())
        builders = [
            ("Поведение", self._build_behavior),
            ("Языки", self._build_languages),
            ("Обучение", self._build_learning),
            ("Раскладка", self._build_layout),
            ("Шрифты", self._build_typography),
            ("Цвета", self._build_colors),
            ("Оверлей", self._build_overlay),
            ("Кнопки", self._build_bindings),
            ("Экран входа", self._build_greeter),
            ("О программе", self._build_about),
        ]
        for title, builder in builders:
            clamp = Adw.Clamp()
            clamp.set_child(builder())
            self._stack.add_titled(clamp, title, title)


def main() -> None:
    app = SettingsApp()
    sys.exit(app.run(sys.argv))
