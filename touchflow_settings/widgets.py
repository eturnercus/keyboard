"""Общие виджеты для страниц настроек."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk


class ColorRow(Gtk.Box):
    def __init__(self, label: str, color: str, on_change):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl = Gtk.Label(label=label)
        lbl.set_hexpand(True)
        lbl.set_xalign(0)
        self.append(lbl)
        btn = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(color)
        btn.set_rgba(rgba)
        btn.connect("color-set", lambda b: on_change(b.get_rgba().to_string()))
        self.append(btn)


class SpinRow(Gtk.Box):
    def __init__(self, label: str, value: int, min_v: int, max_v: int, on_change, step: int = 1):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl = Gtk.Label(label=label)
        lbl.set_hexpand(True)
        lbl.set_xalign(0)
        self.append(lbl)
        spin = Gtk.SpinButton.new_with_range(min_v, max_v, step)
        spin.set_value(value)
        spin.connect("value-changed", lambda s: on_change(int(s.get_value())))
        self.append(spin)


class FloatSpinRow(Gtk.Box):
    """Строка с подписью, опциональным описанием и float SpinButton."""

    def __init__(
        self,
        label: str,
        subtitle: str,
        value: float,
        min_v: float,
        max_v: float,
        on_change,
        step: float = 0.05,
    ):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title = Gtk.Label(label=label, xalign=0)
        title.add_css_class("title-4")
        text_box.append(title)
        if subtitle:
            sub = Gtk.Label(label=subtitle, xalign=0)
            sub.add_css_class("dim-label")
            sub.set_wrap(True)
            text_box.append(sub)
        text_box.set_hexpand(True)
        self.append(text_box)
        spin = Gtk.SpinButton.new_with_range(min_v, max_v, step)
        spin.set_value(value)
        spin.set_digits(2)
        spin.connect("value-changed", lambda s: on_change(s.get_value()))
        self.append(spin)


class SwitchRow(Gtk.Box):
    def __init__(self, label: str, subtitle: str, active: bool, on_change):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title = Gtk.Label(label=label, xalign=0)
        title.add_css_class("title-4")
        box.append(title)
        if subtitle:
            sub = Gtk.Label(label=subtitle, xalign=0)
            sub.add_css_class("dim-label")
            sub.wrap = True
            box.append(sub)
        box.set_hexpand(True)
        self.append(box)
        sw = Gtk.Switch(active=active)
        sw.connect("notify::active", lambda s, _: on_change(s.get_active()))
        self.append(sw)


class EntryRow(Gtk.Box):
    def __init__(self, label: str, value: str, on_change, placeholder: str = ""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl = Gtk.Label(label=label)
        lbl.set_xalign(0)
        lbl.set_width_chars(20)
        self.append(lbl)
        entry = Gtk.Entry()
        entry.set_text(value)
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        entry.connect("changed", lambda e: on_change(e.get_text()))
        self.append(entry)


def page_box() -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    box.set_margin_top(24)
    box.set_margin_bottom(24)
    box.set_margin_start(24)
    box.set_margin_end(24)
    return box
