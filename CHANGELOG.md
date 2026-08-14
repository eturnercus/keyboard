# Changelog

## [1.0.0] - 2026-08-14 (patch 2)

### Fixed
- **touchflow-settings crash**: `FloatSpinRow` принимает subtitle (TypeError: Must be number, not function)
- **PATH**: `~/.local/bin` в `environment.d`, KDE `plasma-workspace/env`, export в install.sh
- **gtk-modules**: авто-удаление из `gtk-4.0/settings.ini` при установке; `touchflow-doctor --fix`


### Python (production)
- Экранная клавиатура GTK4: мультитач, авто-показ (AT-SPI), обучение, оверлей
- Языки RU/EN/UK/DE/FR, быстрые кнопки, F-клавиши, numpad
- `touchflow-settings` — полный GUI настроек (Libadwaita)
- `touchflow-doctor` — диагностика установки
- Абсолютные пути в desktop/systemd (настройки находятся из меню KDE)
- AppImage-установщик, shell-установщик, wheel

### C++ (experimental)
- `touchflowd-cpp`, `touchflow-settings-cpp`
- AppImage-установщик C++

### Удаление
- `scripts/uninstall.sh`, AppImage `TouchFlow-Uninstall`
- `make uninstall`

### Документация
- README.md (русский), README.en.md (английский)
