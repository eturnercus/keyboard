"""CLI для TouchFlow."""

from __future__ import annotations

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="touchflow-cli", description="TouchFlow command line interface")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("show", help="Show keyboard")
    sub.add_parser("hide", help="Hide keyboard")
    sub.add_parser("toggle", help="Toggle keyboard")
    sub.add_parser("reload", help="Reload configuration")
    sub.add_parser("reset-learning", help="Reset learning data")
    sub.add_parser("overlay", help="Toggle gamepad overlay")
    sub.add_parser("status", help="Daemon status via D-Bus")

    args = parser.parse_args()
    commands = {
        "show": ("Show", []),
        "hide": ("Hide", []),
        "toggle": ("Toggle", []),
        "reload": ("ReloadConfig", []),
        "reset-learning": ("ResetLearning", []),
        "overlay": ("ToggleOverlay", []),
    }
    if args.command == "status":
        try:
            from touchflow.dbus_client import dbus_status

            st = dbus_status()
            print(f"version: {st['version']}")
            print(f"visible: {st['visible']}")
            print(f"external_keyboard: {st['external_keyboard']}")
            sys.exit(0)
        except Exception as e:
            print(f"Error: daemon not running or D-Bus unavailable: {e}", file=sys.stderr)
            sys.exit(1)
    if args.command in commands:
        from touchflow.dbus_client import dbus_call

        method, params = commands[args.command]
        try:
            dbus_call(method, *params)
            sys.exit(0)
        except Exception as e:
            print(f"Error: daemon not running or D-Bus unavailable: {e}", file=sys.stderr)
            sys.exit(1)
    parser.print_help()
    sys.exit(1)
