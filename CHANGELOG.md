# Changelog

## [1.0.1] - 2026-08-14

### Fixed
- **Shell-установщик Python** теперь вызывает `scripts/install.sh` (KDE, virtual desktop, systemd)
- **systemd**: убран `GTK_MODULES` (ломал GTK4), добавлен `AT_SPI_BUS_ADDRESS`
- **C++ демон**: исправлен `g_application_run(argc, argv)`, показ клавиатуры при старте
- **C++ AT-SPI**: колбэки в главный поток GTK через `g_idle_add`
- **C++ настройки**: `touchflow-settings-cpp` (GTK4)

### Added
- `scripts/uninstall.sh` — удаление Python и C++ версий
- `systemd/touchflow-daemon-cpp.service`
- Полная интеграция C++ install (systemd, KDE, settings)

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
