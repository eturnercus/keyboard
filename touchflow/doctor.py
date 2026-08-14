"""TouchFlow Doctor — проверка установки."""

from __future__ import annotations

import sys

from touchflow.paths import doctor_report


def main() -> None:
    ok, report = doctor_report()
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
