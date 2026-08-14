"""Тесты paths и doctor."""

from pathlib import Path


def test_patch_desktop_settings_absolute():
    from touchflow.paths import patch_desktop_file
    raw = Path("data/com.touchflow.Settings.desktop").read_text(encoding="utf-8")
    patched = patch_desktop_file(raw)
    assert "Exec=touchflow-settings\n" not in patched
    assert "/touchflow-settings" in patched or ".local/bin" in patched


def test_patch_desktop_virtual_keyboard():
    from touchflow.paths import patch_desktop_file
    raw = Path("data/com.touchflow.Keyboard.Virtual.desktop").read_text(encoding="utf-8")
    patched = patch_desktop_file(raw)
    assert "--virtual-keyboard" in patched
    assert "Exec=touchflowd --virtual-keyboard" not in patched


def test_doctor_runs():
    from touchflow.paths import doctor_report
    ok, text = doctor_report()
    assert "TouchFlow Doctor" in text
    assert "touchflowd" in text
