"""Тесты D-Bus клиента и показа клавиатуры."""

from unittest.mock import MagicMock, patch


def test_try_show_existing_daemon_success():
    from touchflow.dbus_client import try_show_existing_daemon

    with patch("touchflow.dbus_client.dbus_available", return_value=True):
        with patch("touchflow.dbus_client._call_method") as call:
            assert try_show_existing_daemon() is True
            call.assert_called_once_with("Show")


def test_try_show_existing_daemon_failure():
    from touchflow.dbus_client import try_show_existing_daemon

    with patch("touchflow.dbus_client.dbus_available", return_value=False):
        assert try_show_existing_daemon() is False


def test_daemon_virtual_keyboard_forwards_to_existing():
    from touchflow import daemon as daemon_mod

    with patch("touchflow.dbus_client.try_show_existing_daemon", return_value=True) as fwd:
        with patch.object(daemon_mod, "TouchFlowDaemon") as daemon_cls:
            with patch.object(daemon_mod.sys, "exit"):
                with patch.object(daemon_mod.sys, "argv", ["touchflowd", "--virtual-keyboard"]):
                    daemon_mod.main()
    fwd.assert_called_once()
    daemon_cls.assert_not_called()


def test_daemon_virtual_keyboard_starts_when_no_existing():
    from touchflow import daemon as daemon_mod

    with patch("touchflow.dbus_client.try_show_existing_daemon", return_value=False):
        with patch.object(daemon_mod, "TouchFlowDaemon") as daemon_cls:
            inst = MagicMock()
            inst.run.return_value = 0
            daemon_cls.return_value = inst
            with patch.object(daemon_mod.sys, "exit") as exit_mock:
                with patch.object(daemon_mod.sys, "argv", ["touchflowd", "--virtual-keyboard"]):
                    daemon_mod.main()
    daemon_cls.assert_called_once_with(virtual_keyboard=True)
    exit_mock.assert_called_once_with(0)


def test_pluggable_vs_builtin_keyboard_helpers():
    from touchflow.external_kb import has_builtin_keyboard, has_pluggable_keyboard

    sample = (
        'I: Bus=0011 Vendor=0001 Product=0001 Version=ab41\n'
        'N: Name="AT Translated Set 2 keyboard"\n'
        'H: Handlers=kbd event4 \n'
        'B: EV_KEY\n\n'
        'I: Bus=0003 Vendor=046d Product=c31c Version=0111\n'
        'N: Name="Logitech USB Keyboard"\n'
        'H: Handlers=sysrq kbd leds event5 \n'
        'B: EV_KEY\n'
    )
    with patch("touchflow.external_kb.INPUT_DEVICES") as path:
        path.exists.return_value = True
        path.read_text.return_value = sample
        assert has_builtin_keyboard() is True
        assert has_pluggable_keyboard() is True

    builtin_only = (
        'I: Bus=0011 Vendor=0001 Product=0001 Version=ab41\n'
        'N: Name="AT Translated Set 2 keyboard"\n'
        'H: Handlers=kbd event4 \n'
        'B: EV_KEY\n'
    )
    with patch("touchflow.external_kb.INPUT_DEVICES") as path:
        path.exists.return_value = True
        path.read_text.return_value = builtin_only
        assert has_builtin_keyboard() is True
        assert has_pluggable_keyboard() is False
