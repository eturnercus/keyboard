"""Жесты: свайп снизу для показа клавиатуры."""

from __future__ import annotations

import logging
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

log = logging.getLogger(__name__)


class SwipeZone(Gtk.Window):
    """Невидимая зона внизу экрана для свайпа."""

    def __init__(self, zone_height: int, threshold: int, on_swipe_up: Callable[[], None]):
        super().__init__()
        self._threshold = threshold
        self._on_swipe_up = on_swipe_up
        self._start_y = 0.0

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(-1, zone_height)
        self.set_opacity(0.01)

        box = Gtk.Box()
        self.set_child(box)

        self._apply_layer_shell(zone_height)
        self._setup_gesture()

    def _apply_layer_shell(self, height: int) -> None:
        try:
            gi.require_version("Gtk4LayerShell", "1.0")
            from gi.repository import Gtk4LayerShell as LayerShell

            LayerShell.init_for_window(self)
            LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
            LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
            LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
            LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)
            LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, 0)
            LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.NONE)
            LayerShell.set_exclusive_zone(self, height)
        except (ImportError, ValueError):
            self.set_gravity(Gdk.Gravity.SOUTH)

    def _setup_gesture(self) -> None:
        drag = Gtk.GestureDrag.new()
        drag.connect("drag-begin", self._on_drag_begin)
        drag.connect("drag-update", self._on_drag_update)
        self.add_controller(drag)

    def _on_drag_begin(self, gesture, start_x, start_y):
        self._start_y = start_y

    def _on_drag_update(self, gesture, offset_x, offset_y):
        if -offset_y >= self._threshold:
            self._on_swipe_up()
            gesture.reset()
