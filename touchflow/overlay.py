"""Полупрозрачный оверлей с джойстиком и кнопками (режим как на телефонах)."""

from __future__ import annotations

import logging
import math
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk

from touchflow.config import OverlayButton, OverlayConfig, TouchFlowConfig
from touchflow.gtk_compat import connect_pressed, new_press_gesture
from touchflow.key_inject import KeyInjector

log = logging.getLogger(__name__)


class OverlayButtonWidget(Gtk.DrawingArea):
    def __init__(self, btn: OverlayButton, config: OverlayConfig, injector: KeyInjector, on_edit: Callable | None = None):
        super().__init__()
        self.btn = btn
        self._config = config
        self._injector = injector
        self._on_edit = on_edit
        self._pressed = False
        self.set_size_request(btn.width_px, btn.height_px)
        self.set_draw_func(self._draw)
        self.set_opacity(btn.opacity)

        gesture = Gtk.GestureDrag.new()
        gesture.connect("drag-begin", self._on_drag_begin)
        gesture.connect("drag-update", self._on_drag_update)
        gesture.connect("drag-end", self._on_drag_end)
        self.add_controller(gesture)

        press = new_press_gesture(exclusive=True)
        if press is not None:
            connect_pressed(press, self._on_press)
            press.connect("released", self._on_release)
            self.add_controller(press)

        self._drag_start = (0.0, 0.0)

    def _draw(self, area, cr, w, h):
        cr.set_source_rgba(0.2, 0.6, 1.0, self.btn.opacity if not self._pressed else 0.85)
        if self.btn.shape == "circle":
            cr.arc(w / 2, h / 2, min(w, h) / 2 - 2, 0, 2 * math.pi)
        elif self.btn.shape == "diamond":
            cr.move_to(w / 2, 2)
            cr.line_to(w - 2, h / 2)
            cr.line_to(w / 2, h - 2)
            cr.line_to(2, h / 2)
            cr.close_path()
        else:
            cr.rectangle(2, 2, w - 4, h - 4)
        cr.fill_preserve()
        cr.set_source_rgba(1, 1, 1, 0.9)
        cr.set_line_width(2)
        cr.stroke()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(14)
        ext = cr.text_extents(self.btn.label)
        cr.move_to(w / 2 - ext.width / 2, h / 2 + ext.height / 2)
        cr.show_text(self.btn.label)

    def _on_press(self, *_):
        self._pressed = True
        self.queue_draw()
        if self.btn.action == "key" and self.btn.payload:
            self._injector.tap_key(self.btn.payload)

    def _on_release(self, *_):
        self._pressed = False
        self.queue_draw()

    def _on_drag_begin(self, gesture, x, y):
        if not self._config.edit_mode:
            return
        self._drag_start = (x, y)

    def _on_drag_update(self, gesture, ox, oy):
        if not self._config.edit_mode or not self._on_edit:
            return
        self._on_edit(self.btn.id, ox, oy)

    def _on_drag_end(self, *_):
        pass


class JoystickWidget(Gtk.DrawingArea):
    def __init__(self, size: int, opacity: float, on_move: Callable[[float, float], None]):
        super().__init__()
        self._size = size
        self._opacity = opacity
        self._on_move = on_move
        self._stick_x = 0.5
        self._stick_y = 0.5
        self.set_size_request(size, size)
        self.set_draw_func(self._draw)
        self.set_opacity(opacity)

        gesture = Gtk.GestureDrag.new()
        gesture.connect("drag-update", self._on_drag)
        gesture.connect("drag-end", self._on_drag_end)
        self.add_controller(gesture)

    def _draw(self, area, cr, w, h):
        r = min(w, h) / 2
        cx, cy = w / 2, h / 2
        cr.set_source_rgba(0.1, 0.1, 0.1, self._opacity * 0.5)
        cr.arc(cx, cy, r - 2, 0, 2 * math.pi)
        cr.fill()
        cr.set_source_rgba(0.3, 0.7, 1.0, self._opacity)
        cr.arc(cx, cy, r - 8, 0, 2 * math.pi)
        cr.stroke()
        sx = cx + (self._stick_x - 0.5) * (r - 20) * 2
        sy = cy + (self._stick_y - 0.5) * (r - 20) * 2
        cr.set_source_rgba(0.4, 0.8, 1.0, self._opacity + 0.2)
        cr.arc(sx, sy, 18, 0, 2 * math.pi)
        cr.fill()

    def _on_drag(self, gesture, ox, oy):
        w = self.get_allocated_width() or self._size
        h = self.get_allocated_height() or self._size
        self._stick_x = max(0, min(1, (ox + w / 2) / w))
        self._stick_y = max(0, min(1, (oy + h / 2) / h))
        self.queue_draw()
        dx = (self._stick_x - 0.5) * 2
        dy = (self._stick_y - 0.5) * 2
        self._on_move(dx, dy)

    def _on_drag_end(self, *_):
        self._stick_x = 0.5
        self._stick_y = 0.5
        self.queue_draw()
        self._on_move(0, 0)


class OverlayWindow(Gtk.Window):
    def __init__(self, config: TouchFlowConfig, injector: KeyInjector, on_config_change: Callable | None = None):
        super().__init__()
        self._config = config
        self._injector = injector
        self._on_config_change = on_config_change
        self._buttons: dict[str, OverlayButtonWidget] = {}

        self.set_title("TouchFlow Overlay")
        self.set_decorated(False)
        self.set_resizable(False)
        self.fullscreen()
        self.set_opacity(config.overlay.opacity)

        try:
            self.set_modal(False)
        except Exception:
            pass

        overlay = Gtk.Overlay()
        self.set_child(overlay)
        self._container = Gtk.Box()
        overlay.set_child(self._container)

        self._build_widgets()
        self._apply_layer_shell()

    def _apply_layer_shell(self) -> None:
        try:
            gi.require_version("Gtk4LayerShell", "1.0")
            from gi.repository import Gtk4LayerShell as LayerShell

            LayerShell.init_for_window(self)
            LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
            LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
            LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
            LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
            LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)
            LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.NONE)
        except (ImportError, ValueError):
            log.debug("gtk4-layer-shell not available, using standard window")

    def _build_widgets(self) -> None:
        cfg = self._config.overlay
        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0) if display else None
        geo = monitor.get_geometry() if monitor else Gdk.Rectangle(0, 0, 1920, 1080)
        sw, sh = geo.width, geo.height

        fixed = Gtk.Fixed()
        self._container.append(fixed)

        if cfg.joystick_enabled:
            joy = JoystickWidget(cfg.joystick_size_px, cfg.opacity, self._on_joystick)
            joy_x = int(sw * cfg.joystick_x_percent / 100)
            joy_y = int(sh * cfg.joystick_y_percent / 100)
            fixed.put(joy, joy_x, joy_y)

        for btn in cfg.buttons:
            widget = OverlayButtonWidget(btn, cfg, self._injector, self._on_button_edit)
            x = int(sw * btn.x_percent / 100)
            y = int(sh * btn.y_percent / 100)
            fixed.put(widget, x, y)
            self._buttons[btn.id] = widget

    def _on_joystick(self, dx: float, dy: float) -> None:
        threshold = 0.3
        if dx < -threshold:
            self._injector.tap_key("KEY_LEFT")
        elif dx > threshold:
            self._injector.tap_key("KEY_RIGHT")
        if dy < -threshold:
            self._injector.tap_key("KEY_UP")
        elif dy > threshold:
            self._injector.tap_key("KEY_DOWN")

    def _on_button_edit(self, btn_id: str, ox: float, oy: float) -> None:
        if not self._on_config_change:
            return
        for btn in self._config.overlay.buttons:
            if btn.id == btn_id:
                btn.x_percent = max(0, min(100, btn.x_percent + ox / 10))
                btn.y_percent = max(0, min(100, btn.y_percent + oy / 10))
                break
        self._on_config_change(self._config)

    def set_edit_mode(self, enabled: bool) -> None:
        self._config.overlay.edit_mode = enabled

    def apply_config(self, config: TouchFlowConfig) -> None:
        self._config = config
        self.set_opacity(config.overlay.opacity)
