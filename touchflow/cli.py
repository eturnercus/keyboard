"""CLI для TouchFlow."""

from __future__ import annotations

import argparse
import sys


def _dbus_call(method: str, *args):
    try:
        from pydbus import SessionBus

        bus = SessionBus()
        proxy = bus.get("com.touchflow.Keyboard", "/com/touchflow/Keyboard")
        getattr(proxy, method)(*args)
        return 0
    except Exception as e:
        print(f"Error: daemon not running or D-Bus unavailable: {e}", file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="touchflow-cli", description="TouchFlow command line interface")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("show", help="Show keyboard")
    sub.add_parser("hide", help="Hide keyboard")
    sub.add_parser("toggle", help="Toggle keyboard")
    sub.add_parser("reload", help="Reload configuration")
    sub.add_parser("reset-learning", help="Reset learning data")
    sub.add_parser("overlay", help="Toggle gamepad overlay")

    args = parser.parse_args()
    commands = {
        "show": ("Show", []),
        "hide": ("Hide", []),
        "toggle": ("Toggle", []),
        "reload": ("ReloadConfig", []),
        "reset-learning": ("ResetLearning", []),
        "overlay": ("ToggleOverlay", []),
    }
    if args.command in commands:
        method, params = commands[args.command]
        sys.exit(_dbus_call(method, *params))
    parser.print_help()
    sys.exit(1)
