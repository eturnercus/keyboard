from pathlib import Path

def test_virtual_desktop_has_kde_key():
    from pathlib import Path
    text = Path("data/com.touchflow.Keyboard.Virtual.desktop").read_text(encoding="utf-8")
    assert "X-KDE-Wayland-VirtualKeyboard=true" in text
    assert "touchflowd" in text


def test_kde_registration_uses_desktop_basename():
    import inspect
    from touchflow import system_integration
    src = inspect.getsource(system_integration.register_kde_virtual_keyboard)
    assert "desktop_id = virtual_desktop.name" in src
    assert "InputMethod\", desktop_id]" in src


def test_systemd_not_hardcoded_usr():
    text = Path("systemd/touchflow-daemon.service").read_text(encoding="utf-8")
    assert "/usr/bin/touchflowd" not in text
    assert "Type=simple" in text
    assert "GTK_MODULES" not in text
    assert "AT_SPI_BUS_ADDRESS" in text


def test_version_is_1_0_0():
    from touchflow import __version__
    assert __version__ == "1.0.1"


def test_uninstall_script_exists():
    assert Path("scripts/uninstall.sh").exists()
    text = Path("scripts/uninstall.sh").read_text(encoding="utf-8")
    assert "touchflow-daemon-cpp" in text
    assert "touchflow-daemon.service" in text


def test_keyboard_uses_clicked_not_pressed_signal():
    text = Path("touchflow/keyboard_widget.py").read_text(encoding="utf-8")
    assert 'connect("clicked"' in text
    assert 'connect("pressed", self._on_pressed)' not in text


def test_cpp_appimage_builder_exists():
    assert Path("scripts/build-appimage-cpp.sh").exists()
    assert Path("experimental/touchflow-cpp/bundle-install.sh").exists()
