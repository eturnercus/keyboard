"""TouchFlow Doctor — проверка установки."""

from __future__ import annotations

import sys

from touchflow.paths import doctor_report, fix_gtk4_settings_ini


def main() -> None:
    if "--fix" in sys.argv:
        if fix_gtk4_settings_ini():
            print("Исправлено: удалён gtk-modules из ~/.config/gtk-4.0/settings.ini")
        else:
            print("Нечего исправлять в gtk-4.0/settings.ini")
    ok, report = doctor_report()
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
