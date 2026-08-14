"""Тесты запуска демона и D-Bus клиента."""

from unittest.mock import MagicMock, patch


def test_daemon_uses_startup_not_activate():
    text = open("touchflow/daemon.py", encoding="utf-8").read()
    assert 'connect("startup"' in text
    assert "application.hold()" in text
    assert '_setup_services()' in text


def test_dbus_available_uses_name_has_owner():
    with patch("touchflow.dbus_client._name_on_bus", return_value=True):
        from touchflow.dbus_client import dbus_available

        assert dbus_available() is True


def test_ensure_daemon_active_no_dbus_raises():
    from touchflow import dbus_client

    with patch.object(dbus_client, "dbus_available", return_value=False):
        with patch.object(dbus_client, "_systemd_active", return_value=True):
            with patch.object(dbus_client, "_wait_for_dbus", return_value=False):
                with patch.object(dbus_client, "_journal_hint", return_value="test error"):
                    try:
                        dbus_client.ensure_daemon_running(wait_seconds=0.1)
                        assert False, "should raise"
                    except RuntimeError as e:
                        assert "D-Bus не зарегистрирован" in str(e)
