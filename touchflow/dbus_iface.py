"""D-Bus интерфейс для управления демоном из настроек и CLI."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

DBUS_BUS = "com.touchflow.Keyboard"
DBUS_PATH = "/com/touchflow/Keyboard"
DBUS_INTERFACE = "com.touchflow.Keyboard1"

BUS_XML = """
<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <interface name="com.touchflow.Keyboard1">
    <method name="Show"/>
    <method name="Hide"/>
    <method name="Toggle"/>
    <method name="ReloadConfig"/>
    <method name="ResetLearning"/>
    <method name="ToggleOverlay"/>
    <method name="SetOverlayEditMode">
      <arg name="enabled" type="b" direction="in"/>
    </method>
    <property name="Visible" type="b" access="read"/>
    <property name="ExternalKeyboardConnected" type="b" access="read"/>
    <property name="Version" type="s" access="read"/>
  </interface>
</node>
"""


class TouchFlowDBusService:
    def __init__(self, daemon):
        self._daemon = daemon
        self._bus = None

    def publish(self) -> bool:
        try:
            from pydbus import SessionBus

            self._bus = SessionBus()
            self._bus.publish(DBUS_BUS, self)
            log.info("D-Bus service published: %s", DBUS_BUS)
            return True
        except Exception as e:
            log.warning("D-Bus unavailable: %s", e)
            return False

    # D-Bus methods
    def Show(self):
        self._daemon.show_keyboard(manual=True)

    def Hide(self):
        self._daemon.hide_keyboard(manual=True)

    def Toggle(self):
        self._daemon.toggle_keyboard()

    def ReloadConfig(self):
        self._daemon.reload_config()

    def ResetLearning(self):
        self._daemon.reset_learning()

    def ToggleOverlay(self):
        self._daemon.toggle_overlay()

    def SetOverlayEditMode(self, enabled: bool):
        self._daemon.set_overlay_edit_mode(enabled)

    @property
    def Visible(self) -> bool:
        return self._daemon.visible

    @property
    def ExternalKeyboardConnected(self) -> bool:
        return self._daemon.external_keyboard_connected

    @property
    def Version(self) -> str:
        from touchflow import __version__
        return __version__
