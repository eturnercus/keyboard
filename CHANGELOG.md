# Changelog

## [1.0.0] - 2026-08-14

Единый релиз **1.0.0** — Python (основная) и C++ (экспериментальная).

### Python 1.0.0 (production)

- Экранная клавиатура GTK4 с мультитачем, авто-показом (AT-SPI), обучением
- Языки: RU, EN, UK, DE, FR
- Быстрые кнопки: копировать, вставить, вырезать, выделить всё, отмена, повтор, поиск
- Оверлей/джойстик, физические привязки, greeter, D-Bus API
- Настройки (GTK4/Libadwaita), первый запуск, systemd user service
- AppImage-установщик, shell-установщик, wheel, sdist
- **Исправлено**: GTK4 `TypeError` на `connect("pressed")` → `clicked` + gesture
- **Исправлено**: systemd путь `~/.local/bin/touchflowd`, `Type=simple`
- **Исправлено**: AppImage ELF (x86_64 + aarch64)
- **Исправлено**: KDE «Виртуальные клавиатуры» — desktop + kwinrc InputMethod

### C++ 1.0.0 (experimental)

- `experimental/touchflow-cpp/` — нативный демон `touchflowd-cpp`
- GTK4 + libadwaita, uinput/evdev, AT-SPI авто-показ
- Раскладки RU/EN, быстрые действия, обучение, внешняя клавиатура
- KDE virtual keyboard desktop, install script
