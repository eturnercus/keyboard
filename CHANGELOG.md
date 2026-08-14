# Changelog

## [1.0.1] - 2026-08-14

### Fixed
- **Клавиатура не показывалась**: `present()` на Wayland, режим `--virtual-keyboard` (KDE) перенаправляет Show в уже запущенный демон
- **Встроенная клавиатура ноутбука** больше не блокирует авто-показ (только USB/BT)
- **touchflow-doctor**: проверка демона, D-Bus, AT-SPI, gtk4-layer-shell, KDE InputMethod
- **touchflow-settings**: кнопки «Показать клавиатуру» / «Скрыть»
- **Установка**: зависимости layer-shell, проверка D-Bus после старта демона

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
