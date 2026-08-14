"""Совместимость GTK4 между версиями (Debian 12/13, GNOME 46+)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def new_press_gesture(*, exclusive: bool = False):
    """Жест нажатия: GestureMultiPress (GTK ≤4.8) или GestureClick (GTK ≥4.10)."""
    if hasattr(Gtk, "GestureMultiPress"):
        gesture = Gtk.GestureMultiPress.new()
    elif hasattr(Gtk, "GestureClick"):
        gesture = Gtk.GestureClick.new()
    else:
        return None
    gesture.set_exclusive(exclusive)
    return gesture


def connect_pressed(gesture, callback) -> None:
    """Подключить обработчик pressed (n_press, x, y)."""
    gesture.connect("pressed", callback)
