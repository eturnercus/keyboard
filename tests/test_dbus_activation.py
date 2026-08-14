"""Тесты D-Bus activation и автозапуска демона."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from touchflow.dbus_iface import BUS_XML, TouchFlowDBusService


def test_dbus_service_has_introspection_xml():
    assert TouchFlowDBusService.dbus == BUS_XML
    assert 'method name="Show"' in TouchFlowDBusService.dbus


def test_install_dbus_service_writes_file(tmp_path, monkeypatch):
    from touchflow import paths

    monkeypatch.setattr(paths, "home", lambda: tmp_path)
    monkeypatch.setattr(paths, "resolve_cmd", lambda name: f"/home/test/.local/bin/{name}")

    dst = paths.install_dbus_service()
    assert dst.exists()
    text = dst.read_text(encoding="utf-8")
    assert "Name=com.touchflow.Keyboard" in text
    assert "/home/test/.local/bin/touchflowd" in text


def test_ensure_daemon_running_uses_systemctl_when_available():
    from touchflow import dbus_client

    with patch.object(dbus_client, "dbus_available", side_effect=[False, True]):
        with patch.object(dbus_client, "_systemd_active", return_value=False):
            with patch.object(dbus_client.shutil, "which", return_value="/usr/bin/systemctl"):
                with patch.object(dbus_client.subprocess, "run") as run:
                    dbus_client.ensure_daemon_running(wait_seconds=0.5)
                    assert any("start" in str(c) for c in run.call_args_list)


def test_dbus_show_calls_method():
    from touchflow import dbus_client

    with patch.object(dbus_client, "ensure_daemon_running"):
        with patch.object(dbus_client, "_call_method") as call:
            dbus_client.dbus_show()
            call.assert_called_once_with("Show")


def test_try_show_existing_daemon_success():
    from touchflow import dbus_client

    with patch.object(dbus_client, "dbus_available", return_value=True):
        with patch.object(dbus_client, "_call_method") as call:
            assert dbus_client.try_show_existing_daemon() is True
            call.assert_called_once_with("Show")
