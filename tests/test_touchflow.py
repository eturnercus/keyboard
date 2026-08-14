"""Tests for TouchFlow."""

import tempfile
from pathlib import Path

import pytest

from touchflow.config import (
    AppLearningRule,
    LanguageEntry,
    TouchFlowConfig,
    factory_reset,
    load_config,
    save_config,
)
from touchflow.external_kb import list_keyboards, has_external_keyboard
from touchflow.learning import LearningEngine
from touchflow.layouts import available_languages, get_layout_rows
from touchflow.onboarding import is_first_run, mark_first_run_complete, reset_first_run_flag


def test_default_config():
    cfg = TouchFlowConfig()
    assert cfg.behavior.auto_show is True
    assert cfg.learning.enabled is True
    assert len(cfg.get_enabled_languages()) >= 2


def test_config_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        cfg = TouchFlowConfig()
        cfg.layout.height_px = 350
        cfg.learning.threshold = 0.5
        save_config(cfg, path)
        loaded = load_config(path)
        assert loaded.layout.height_px == 350
        assert loaded.learning.threshold == 0.5


def test_languages():
    cfg = TouchFlowConfig()
    assert cfg.get_default_language() == "ru"
    assert cfg.next_language("ru") == "en"
    assert cfg.next_language("en") == "ru"


def test_add_language():
    cfg = TouchFlowConfig()
    cfg.languages.entries.append(LanguageEntry("uk", "Українська", True, False))
    enabled = [e.code for e in cfg.get_enabled_languages()]
    assert "uk" in enabled


def test_layouts():
    assert "ru" in available_languages()
    assert "en" in available_languages()
    rows = get_layout_rows("ru")
    assert len(rows) == 3


def test_learning_rules():
    engine = LearningEngine(config=TouchFlowConfig().learning)
    engine.rules.append(AppLearningRule("firefox", "", "always_hide"))
    assert engine.should_auto_show("firefox", "navigator") is False
    engine.rules = [AppLearningRule("gedit", "", "always_show")]
    assert engine.should_auto_show("gedit", "GtkWindow") is True


def test_learning_should_show():
    engine = LearningEngine(config=TouchFlowConfig().learning)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    assert engine.should_auto_show("firefox", "navigator") is False


def test_first_run():
    import touchflow.config as cfg_mod
    import touchflow.onboarding as onboard_mod

    with tempfile.TemporaryDirectory() as tmp:
        orig = cfg_mod.FIRST_RUN_PATH
        cfg_mod.FIRST_RUN_PATH = Path(tmp) / ".first_run_done"
        onboard_mod.FIRST_RUN_PATH = cfg_mod.FIRST_RUN_PATH
        assert is_first_run() is True
        mark_first_run_complete()
        assert is_first_run() is False
        reset_first_run_flag()
        assert is_first_run() is True
        cfg_mod.FIRST_RUN_PATH = orig
        onboard_mod.FIRST_RUN_PATH = orig


def test_external_keyboard_list():
    devices = list_keyboards()
    assert isinstance(devices, list)


def test_quick_actions_config():
    cfg = TouchFlowConfig()
    assert cfg.layout.show_quick_actions is True


def test_chord_methods_exist():
    from touchflow.key_inject import KeyInjector
    inj = KeyInjector.__new__(KeyInjector)
    for method in ("copy", "paste", "cut", "select_all", "undo", "redo", "find", "chord"):
        assert hasattr(inj, method)


def test_quick_actions_defined():
    from touchflow.keyboard_widget import ACTION_HANDLERS, QUICK_ACTIONS
    assert len(QUICK_ACTIONS) >= 5
    assert "ACTION_COPY" in ACTION_HANDLERS
    assert ACTION_HANDLERS["ACTION_PASTE"] == "paste"
