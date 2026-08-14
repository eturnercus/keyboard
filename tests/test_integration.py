from pathlib import Path

def test_virtual_desktop_has_kde_key():
    from pathlib import Path
    text = Path("data/com.touchflow.Keyboard.Virtual.desktop").read_text(encoding="utf-8")
    assert "X-KDE-Wayland-VirtualKeyboard=true" in text
    assert "touchflowd" in text


def test_systemd_not_hardcoded_usr():
    text = Path("systemd/touchflow-daemon.service").read_text(encoding="utf-8")
    assert "/usr/bin/touchflowd" not in text
    assert "Type=simple" in text
