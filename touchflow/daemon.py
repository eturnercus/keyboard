"""Главный демон TouchFlow."""

from __future__ import annotations

import logging
import sys
import time
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, GLib, Gtk

from touchflow import __version__, APP_ID
from touchflow.config import TouchFlowConfig, load_config, save_config
from touchflow.dbus_iface import TouchFlowDBusService
from touchflow.external_kb import ExternalKeyboardMonitor
from touchflow.focus_watcher import FocusInfo, FocusWatcher
from touchflow.gestures import SwipeZone
from touchflow.keyboard_widget import KeyboardWidget
from touchflow.key_inject import KeyInjector
from touchflow.learning import LearningEngine
from touchflow.overlay import OverlayWindow
from touchflow.physical_bindings import PhysicalButtonListener

if TYPE_CHECKING:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("touchflowd")


class TouchFlowDaemon:
    def __init__(self):
        self.config = load_config()
        self.injector = KeyInjector()
        self.learning = LearningEngine(
            enabled=self.config.behavior.learning_enabled,
            show_weight=self.config.behavior.show_learning_weight,
            dismiss_weight=self.config.behavior.dismiss_learning_weight,
        )
        self.kb_monitor = ExternalKeyboardMonitor(on_change=self._on_external_kb_change)
        self.focus_watcher = FocusWatcher(self._on_focus_change)

        self._window: Gtk.Window | None = None
        self._keyboard: KeyboardWidget | None = None
        self._overlay: OverlayWindow | None = None
        self._swipe_zone: SwipeZone | None = None
        self._physical: PhysicalButtonListener | None = None
        self._dbus: TouchFlowDBusService | None = None

        self._visible = False
        self._current_focus = FocusInfo()
        self._show_time = 0.0
        self._manual_show = False

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def external_keyboard_connected(self) -> bool:
        return self.kb_monitor.connected

    def run(self) -> int:
        app = Gtk.Application(application_id=APP_ID)

        def on_activate(application):
            self._setup_ui()
            self._setup_services()
            if not self.config.behavior.startup_hidden:
                self.show_keyboard()

        app.connect("activate", on_activate)
        return app.run(sys.argv)

    def _setup_ui(self) -> None:
        cfg = self.config

        self._window = Gtk.Window()
        self._window.set_title("TouchFlow")
        self._window.set_decorated(False)
        self._window.set_resizable(False)
        self._window.set_default_size(-1, cfg.layout.height_px)
        self._apply_keyboard_layer_shell()

        self._keyboard = KeyboardWidget(cfg, self.injector, self._on_keyboard_action)
        self._window.set_child(self._keyboard)

        if cfg.behavior.startup_hidden:
            self._window.set_visible(False)
        else:
            self._visible = True

        if cfg.behavior.swipe_from_bottom:
            self._swipe_zone = SwipeZone(
                cfg.behavior.swipe_zone_height_px,
                cfg.behavior.swipe_threshold_px,
                lambda: self.show_keyboard(manual=True),
            )
            self._swipe_zone.set_visible(True)

        if cfg.overlay.enabled:
            self._show_overlay()

    def _apply_keyboard_layer_shell(self) -> None:
        try:
            gi.require_version("Gtk4LayerShell", "1.0")
            from gi.repository import Gtk4LayerShell as LayerShell

            LayerShell.init_for_window(self._window)
            LayerShell.set_layer(self._window, LayerShell.Layer.OVERLAY)
            LayerShell.set_anchor(self._window, LayerShell.Edge.BOTTOM, True)
            LayerShell.set_anchor(self._window, LayerShell.Edge.LEFT, True)
            LayerShell.set_anchor(self._window, LayerShell.Edge.RIGHT, True)
            LayerShell.set_keyboard_mode(self._window, LayerShell.KeyboardMode.ON_DEMAND)
            if self.config.behavior.dock_bottom:
                LayerShell.set_exclusive_zone(self._window, self.config.layout.height_px)
        except (ImportError, ValueError):
            log.info("gtk4-layer-shell not found — using standard window placement")

    def _setup_services(self) -> None:
        self.focus_watcher.start()
        self._dbus = TouchFlowDBusService(self)
        self._dbus.publish()

        bindings = {
            "grab_device": self.config.bindings.grab_device,
            "toggle_visibility": self.config.bindings.toggle_visibility,
            "show_keyboard": self.config.bindings.show_keyboard,
            "hide_keyboard": self.config.bindings.hide_keyboard,
            "switch_layout": self.config.bindings.switch_layout,
            "toggle_overlay": self.config.bindings.toggle_overlay,
        }
        self._physical = PhysicalButtonListener(bindings, self._on_physical_action)
        self._physical.start()

        GLib.timeout_add_seconds(2, self._poll_external_kb)
        log.info("TouchFlow %s started", __version__)

    def _poll_external_kb(self) -> bool:
        self.kb_monitor.poll()
        return True

    def _on_external_kb_change(self, connected: bool) -> None:
        log.info("External keyboard %s", "connected" if connected else "disconnected")
        cfg = self.config.behavior
        if connected and cfg.hide_on_external_keyboard and self._visible:
            self.hide_keyboard()
        elif not connected and cfg.show_on_external_keyboard_disconnect and self._current_focus.is_text_entry:
            if not cfg.hide_on_external_keyboard or not connected:
                self.show_keyboard()

    def _on_focus_change(self, info: FocusInfo) -> None:
        self._current_focus = info
        if not info.is_text_entry:
            if self.config.behavior.auto_hide_on_blur and self._visible and not self._manual_show:
                self.hide_keyboard()
            return

        if info.app_id in self.config.excluded_apps:
            return
        if info.window_class in self.config.excluded_window_classes:
            return

        if self.config.behavior.hide_on_external_keyboard and self.kb_monitor.connected:
            return

        if not self.config.behavior.auto_show:
            return

        if not self.learning.should_auto_show(info.app_id, info.window_class):
            log.debug("Learning blocked auto-show for %s", info.app_id)
            return

        self.show_keyboard()
        self.learning.on_auto_show(info.app_id, info.window_class)

    def show_keyboard(self, manual: bool = False) -> None:
        if self.config.behavior.hide_on_external_keyboard and self.kb_monitor.connected:
            if not manual:
                return

        if self._window:
            self._window.set_visible(True)
            self._visible = True
            self._show_time = time.time()
            self._manual_show = manual
            if manual:
                self.learning.on_manual_show(
                    self._current_focus.app_id,
                    self._current_focus.window_class,
                )

    def hide_keyboard(self, manual: bool = False) -> None:
        if self._window:
            immediate = manual and (time.time() - self._show_time) < 1.5
            self.learning.on_dismiss(
                self._current_focus.app_id,
                self._current_focus.window_class,
                immediate=immediate,
            )
            self._window.set_visible(False)
            self._visible = False
            self._manual_show = False

    def toggle_keyboard(self) -> None:
        if self._visible:
            self.hide_keyboard(manual=True)
        else:
            self.show_keyboard(manual=True)

    def reload_config(self) -> None:
        self.config = load_config()
        self.learning = LearningEngine(
            enabled=self.config.behavior.learning_enabled,
            show_weight=self.config.behavior.show_learning_weight,
            dismiss_weight=self.config.behavior.dismiss_learning_weight,
        )
        if self._keyboard:
            self._keyboard.apply_config(self.config)
        if self._overlay:
            self._overlay.apply_config(self.config)
        log.info("Config reloaded")

    def reset_learning(self) -> None:
        self.learning.reset()
        log.info("Learning data reset")

    def toggle_overlay(self) -> None:
        if self._overlay:
            visible = self._overlay.get_visible()
            self._overlay.set_visible(not visible)
        else:
            self._show_overlay()

    def set_overlay_edit_mode(self, enabled: bool) -> None:
        if self._overlay:
            self._overlay.set_edit_mode(enabled)

    def _show_overlay(self) -> None:
        self._overlay = OverlayWindow(
            self.config,
            self.injector,
            on_config_change=lambda c: save_config(c),
        )
        self._overlay.set_visible(True)

    def _on_keyboard_action(self, action: str, detail: str = "") -> None:
        if action == "hide":
            self.hide_keyboard(manual=True)

    def _on_physical_action(self, action: str) -> None:
        GLib.idle_add(self._dispatch_physical, action)

    def _dispatch_physical(self, action: str) -> bool:
        handlers = {
            "toggle": self.toggle_keyboard,
            "show_keyboard": lambda: self.show_keyboard(manual=True),
            "hide_keyboard": lambda: self.hide_keyboard(manual=True),
            "toggle_overlay": self.toggle_overlay,
        }
        fn = handlers.get(action)
        if fn:
            fn()
        return False


def main() -> None:
    daemon = TouchFlowDaemon()
    sys.exit(daemon.run())
