"""Конфигурация TouchFlow — единый источник правды для всех настроек."""

from __future__ import annotations

import copy
import os
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import tomli_w

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "touchflow"
CONFIG_PATH = CONFIG_DIR / "config.toml"
LEARNING_PATH = CONFIG_DIR / "learning.json"
OVERLAY_PATH = CONFIG_DIR / "overlay.toml"
FIRST_RUN_PATH = CONFIG_DIR / ".first_run_done"


def _hex(color: str) -> str:
    return color if color.startswith("#") else f"#{color}"


@dataclass
class Colors:
    background: str = "#1e1e2e"
    key_background: str = "#313244"
    key_pressed: str = "#89b4fa"
    key_text: str = "#cdd6f4"
    accent: str = "#cba6f7"
    border: str = "#45475a"


@dataclass
class Typography:
    font_family: str = "Sans"
    font_size: int = 14
    label_size: int = 11
    bold_labels: bool = False


@dataclass
class Layout:
    height_px: int = 280
    width_percent: int = 100
    key_spacing: int = 4
    key_radius: int = 8
    row_height: int = 52
    show_number_row: bool = True
    show_function_row: bool = True
    show_arrow_row: bool = True
    show_numpad: bool = False
    numpad_side: str = "right"  # left | right
    compact_mode: bool = False
    show_quick_actions: bool = True


@dataclass
class Behavior:
    auto_show: bool = True
    auto_hide_on_blur: bool = True
    hide_on_external_keyboard: bool = True
    show_on_external_keyboard_disconnect: bool = True
    swipe_from_bottom: bool = True
    swipe_zone_height_px: int = 24
    swipe_threshold_px: int = 80
    learning_enabled: bool = True
    dismiss_learning_weight: float = 1.0
    show_learning_weight: float = 0.5
    startup_hidden: bool = True
    remember_position: bool = True
    dock_bottom: bool = True
    animation_ms: int = 200
    haptic_feedback: bool = False
    click_sound: bool = False
    long_press_repeat: bool = True
    long_press_delay_ms: int = 400
    multitouch_enabled: bool = True
    max_simultaneous_keys: int = 10


@dataclass
class PhysicalBindings:
    """Привязка физических кнопок к действиям TouchFlow."""

    toggle_visibility: list[str] = field(default_factory=lambda: ["KEY_F23"])
    show_keyboard: list[str] = field(default_factory=list)
    hide_keyboard: list[str] = field(default_factory=list)
    switch_layout: list[str] = field(default_factory=list)
    toggle_overlay: list[str] = field(default_factory=list)
    grab_device: str = ""  # путь evdev, пусто = не перехватывать


@dataclass
class OverlayButton:
    id: str
    label: str
    x_percent: float
    y_percent: float
    width_px: int
    height_px: int
    opacity: float = 0.55
    action: str = "key"  # key | mouse | script
    payload: str = ""
    shape: str = "circle"  # circle | rect | diamond


@dataclass
class OverlayConfig:
    enabled: bool = False
    opacity: float = 0.6
    edit_mode: bool = False
    joystick_enabled: bool = True
    joystick_x_percent: float = 8.0
    joystick_y_percent: float = 70.0
    joystick_size_px: int = 140
    buttons: list[OverlayButton] = field(default_factory=lambda: [
        OverlayButton("btn_a", "A", 85.0, 75.0, 64, 64, payload="KEY_A"),
        OverlayButton("btn_b", "B", 92.0, 62.0, 56, 56, payload="KEY_B"),
        OverlayButton("btn_x", "X", 78.0, 62.0, 56, 56, payload="KEY_X"),
        OverlayButton("btn_y", "Y", 85.0, 50.0, 56, 56, payload="KEY_Y"),
        OverlayButton("btn_l1", "L1", 5.0, 35.0, 72, 40, payload="KEY_Q"),
        OverlayButton("btn_r1", "R1", 90.0, 35.0, 72, 40, payload="KEY_E"),
    ])


@dataclass
class LanguageEntry:
    code: str = "ru"
    name: str = "Русский"
    enabled: bool = True
    is_default: bool = False


@dataclass
class LanguagesConfig:
    """Управление языками клавиатуры."""

    entries: list[LanguageEntry] = field(default_factory=lambda: [
        LanguageEntry("ru", "Русский", True, True),
        LanguageEntry("en", "English", True, False),
    ])
    show_switch_key: bool = True
    switch_key_label: str = "🌐"
    show_current_lang_on_key: bool = True
    cycle_on_switch: bool = True


@dataclass
class AppLearningRule:
    """Ручное правило: где показывать клавиатуру."""

    app_id: str = ""
    window_class: str = ""
    mode: str = "auto"  # auto | always_show | always_hide


@dataclass
class LearningConfig:
    enabled: bool = True
    threshold: float = 0.35
    dismiss_weight: float = 1.0
    show_weight: float = 0.5
    rules: list[AppLearningRule] = field(default_factory=list)


@dataclass
class FirstRunConfig:
    onboarding_completed: bool = False


@dataclass
class LocaleLayout:
    """Устаревшее — используйте languages. Оставлено для совместимости."""

    name: str = "ru"
    primary: str = "ru"
    secondary: str = "en"
    show_language_switch: bool = True


@dataclass
class Greeter:
    """Работа до входа в систему (GDM/LightDM/SDDM)."""

    enabled: bool = True
    user: str = "touchflow"
    display: str = ":0"


@dataclass
class TouchFlowConfig:
    version: int = 2
    colors: Colors = field(default_factory=Colors)
    typography: Typography = field(default_factory=Typography)
    layout: Layout = field(default_factory=Layout)
    behavior: Behavior = field(default_factory=Behavior)
    bindings: PhysicalBindings = field(default_factory=PhysicalBindings)
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    languages: LanguagesConfig = field(default_factory=LanguagesConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    first_run: FirstRunConfig = field(default_factory=FirstRunConfig)
    locale: LocaleLayout = field(default_factory=LocaleLayout)
    greeter: Greeter = field(default_factory=Greeter)
    custom_css: str = ""
    excluded_apps: list[str] = field(default_factory=lambda: ["touchflow-settings"])
    excluded_window_classes: list[str] = field(default_factory=list)

    def get_enabled_languages(self) -> list[LanguageEntry]:
        return [e for e in self.languages.entries if e.enabled]

    def get_default_language(self) -> str:
        for e in self.languages.entries:
            if e.enabled and e.is_default:
                return e.code
        enabled = self.get_enabled_languages()
        return enabled[0].code if enabled else "en"

    def next_language(self, current: str) -> str:
        enabled = [e.code for e in self.get_enabled_languages()]
        if not enabled:
            return current
        if current not in enabled:
            return enabled[0]
        idx = enabled.index(current)
        return enabled[(idx + 1) % len(enabled)]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TouchFlowConfig":
        cfg = cls()
        for section_name, section_cls in [
            ("colors", Colors),
            ("typography", Typography),
            ("layout", Layout),
            ("behavior", Behavior),
            ("bindings", PhysicalBindings),
            ("locale", LocaleLayout),
            ("greeter", Greeter),
            ("first_run", FirstRunConfig),
        ]:
            if section_name in data and isinstance(data[section_name], dict):
                for key, value in data[section_name].items():
                    if hasattr(getattr(cfg, section_name), key):
                        setattr(getattr(cfg, section_name), key, value)
        if "languages" in data and isinstance(data["languages"], dict):
            ld = data["languages"]
            langs = LanguagesConfig()
            for key, value in ld.items():
                if key == "entries" and isinstance(value, list):
                    langs.entries = [LanguageEntry(**e) for e in value]
                elif hasattr(langs, key):
                    setattr(langs, key, value)
            cfg.languages = langs
        if "learning" in data and isinstance(data["learning"], dict):
            lnd = data["learning"]
            learn = LearningConfig()
            for key, value in lnd.items():
                if key == "rules" and isinstance(value, list):
                    learn.rules = [AppLearningRule(**r) for r in value]
                elif hasattr(learn, key):
                    setattr(learn, key, value)
            cfg.learning = learn
        if "overlay" in data and isinstance(data["overlay"], dict):
            od = data["overlay"]
            overlay = OverlayConfig()
            for key, value in od.items():
                if key == "buttons" and isinstance(value, list):
                    overlay.buttons = [OverlayButton(**b) for b in value]
                elif hasattr(overlay, key):
                    setattr(overlay, key, value)
            cfg.overlay = overlay
        for key in ("custom_css", "excluded_apps", "excluded_window_classes", "version"):
            if key in data:
                setattr(cfg, key, data[key])
        # Миграция v1 → v2: behavior.learning_* → learning.*
        if "behavior" in data and isinstance(data["behavior"], dict):
            b = data["behavior"]
            if "learning_enabled" in b:
                cfg.learning.enabled = b["learning_enabled"]
            if "show_learning_weight" in b:
                cfg.learning.show_weight = b["show_learning_weight"]
            if "dismiss_learning_weight" in b:
                cfg.learning.dismiss_weight = b["dismiss_learning_weight"]
        return cfg


DEFAULT_CONFIG = TouchFlowConfig()


def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config(path: Path | None = None) -> TouchFlowConfig:
    path = path or CONFIG_PATH
    if not path.exists():
        ensure_config_dir()
        save_config(DEFAULT_CONFIG, path)
        return copy.deepcopy(DEFAULT_CONFIG)
    with path.open("rb") as f:
        data = tomllib.load(f)
    return TouchFlowConfig.from_dict(data)


def save_config(config: TouchFlowConfig, path: Path | None = None) -> None:
    path = path or CONFIG_PATH
    ensure_config_dir()
    tmp = path.with_suffix(".tmp")
    with tmp.open("wb") as f:
        tomli_w.dump(config.to_dict(), f)
    tmp.replace(path)


def reset_config() -> TouchFlowConfig:
    if CONFIG_PATH.exists():
        backup = CONFIG_PATH.with_suffix(".toml.bak")
        shutil.copy2(CONFIG_PATH, backup)
    if LEARNING_PATH.exists():
        LEARNING_PATH.unlink(missing_ok=True)
    if FIRST_RUN_PATH.exists():
        FIRST_RUN_PATH.unlink(missing_ok=True)
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    save_config(cfg)
    return cfg


def factory_reset() -> TouchFlowConfig:
    """Полный сброс: настройки, обучение, флаг первого запуска."""
    return reset_config()


def export_config(dest: Path) -> None:
    save_config(load_config(), dest)


def import_config(src: Path) -> TouchFlowConfig:
    cfg = load_config(src)
    save_config(cfg)
    return cfg
