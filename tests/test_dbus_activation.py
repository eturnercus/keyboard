"""Тесты D-Bus activation и автозапуска демона."""

from pathlib import Path
from unittest.mock import MagicMock, patch


def test_install_dbus_service_writes_file(tmp_path, monkeypatch):
    from touchflow import paths

    monkeypatch.setattr(paths, "home", lambda: tmp_path)
    monkeypatch.setattr(paths, "resolve_cmd", lambda name: f"/home/test/.local/bin/{name}")

    template = Path("data/com.touchflow.Keyboard.service")
    dst = paths.install_dbus_service()
    assert dst.exists()
    text = dst.read_text(encoding="utf-8")
    assert "Name=com.touchflow.Keyboard" in text
    assert "/home/test/.local/bin/touchflowd" in text


def test_ensure_daemon_running_uses_systemctl_when_available():
    from touchflow import dbus_client

    with patch.object(dbus_client, "dbus_available", side_effect=[False, True]):
        with patch.object(dbus_client.shutil, "which", return_value="/usr/bin/systemctl"):
            with patch.object(dbus_client.subprocess, "run") as run:
                dbus_client.ensure_daemon_running(wait_seconds=1)
                run.assert_called_once()
                assert "systemctl" in run.call_args[0][0]


def test_ensure_daemon_running_spawns_touchflowd():
    from touchflow import dbus_client

    with patch.object(dbus_client, "dbus_available", side_effect=[False, False, True]):
        with patch.object(dbus_client.shutil, "which", return_value=None):
            with patch.object(dbus_client, "_touchflowd_path", return_value="/bin/touchflowd"):
                with patch("touchflow.dbus_client.Path") as path_cls:
                    path_cls.return_value.exists.return_value = True
                    with patch.object(dbus_client.subprocess, "Popen") as popen:
                        dbus_client.ensure_daemon_running(wait_seconds=0.6)
                        popen.assert_called_once()
