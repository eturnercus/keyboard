"""Tests for TouchFlow."""

import tempfile
from pathlib import Path

import pytest

from touchflow.config import TouchFlowConfig, load_config, save_config, reset_config, DEFAULT_CONFIG
from touchflow.external_kb import list_keyboards, has_external_keyboard
from touchflow.learning import LearningEngine, LearningStore


def test_default_config():
    cfg = TouchFlowConfig()
    assert cfg.behavior.auto_show is True
    assert cfg.behavior.hide_on_external_keyboard is True
    assert cfg.layout.show_function_row is True


def test_config_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.toml"
        cfg = TouchFlowConfig()
        cfg.layout.height_px = 350
        cfg.colors.background = "#000000"
        save_config(cfg, path)
        loaded = load_config(path)
        assert loaded.layout.height_px == 350
        assert loaded.colors.background == "#000000"


def test_config_from_dict():
    data = {
        "behavior": {"auto_show": False, "multitouch_enabled": False},
        "layout": {"height_px": 200},
    }
    cfg = TouchFlowConfig.from_dict(data)
    assert cfg.behavior.auto_show is False
    assert cfg.layout.height_px == 200


def test_learning_should_show():
    engine = LearningEngine(enabled=True)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    engine.on_dismiss("firefox", "navigator", immediate=True)
    assert engine.should_auto_show("firefox", "navigator") is False


def test_learning_manual_show():
    engine = LearningEngine(enabled=True)
    engine.on_dismiss("gedit", "gedit", immediate=True)
    engine.on_manual_show("gedit", "gedit")
    engine.on_manual_show("gedit", "gedit")
    assert engine.should_auto_show("gedit", "gedit") is True


def test_learning_store_persistence():
    with tempfile.TemporaryDirectory() as tmp:
        import touchflow.config as cfg_mod
        import touchflow.learning as learn_mod

        orig = cfg_mod.LEARNING_PATH
        cfg_mod.LEARNING_PATH = Path(tmp) / "learning.json"
        learn_mod.LEARNING_PATH = cfg_mod.LEARNING_PATH

        engine = LearningEngine()
        engine.on_show = engine.on_auto_show
        engine.on_auto_show("test", "window")
        engine2 = LearningEngine()
        assert "test|window" in engine2.store.patterns

        cfg_mod.LEARNING_PATH = orig
        learn_mod.LEARNING_PATH = orig


def test_external_keyboard_list():
    devices = list_keyboards()
    assert isinstance(devices, list)


def test_external_keyboard_detection():
    result = has_external_keyboard()
    assert isinstance(result, bool)
