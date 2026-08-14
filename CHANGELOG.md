# Changelog

## [1.0.0] - 2026-08-14

Единый стабильный релиз TouchFlow Keyboard.

### Fixed (2026-08-14 patch 3)
- **Установка падала**: `NameError: os` в `ensure_atspi_bus()`

### Fixed (2026-08-14 patch 2)
- **Демон падал на Debian 13 / GTK 4.18**: `GestureMultiPress` заменён на `GestureClick` через `gtk_compat`
- **AT-SPI bus**: предупреждение вместо ошибки; автозапуск `at-spi-dbus-bus.service` при установке

### Fixed (2026-08-14 patch)
- **D-Bus Show**: `dbus = BUS_XML` на сервере + клиент через dbus-python (исправлен CompositeObject)
- **python3-dbus** в зависимостях установки
- **D-Bus / демон**: activation-файл `com.touchflow.Keyboard.service`, автозапуск демона из настроек и CLI
- **systemctl --user**: корректные переменные среды, `import-environment`; предупреждение не использовать `sudo`
- **touchflow-settings crash**: `FloatSpinRow` + subtitle
- **PATH**: `~/.local/bin` в environment.d и KDE plasma env
- **Показ клавиатуры**: `present()` на Wayland, KDE `--virtual-keyboard` → D-Bus Show
- **Встроенная клавиатура** ноутбука не блокирует авто-показ (только USB/BT)
- **touchflow-doctor**: демон, D-Bus, AT-SPI, layer-shell, KDE InputMethod
- **Кнопки** «Показать клавиатуру» / «Скрыть» в настройках
- **gtk-modules** авто-удаление из gtk-4.0/settings.ini
- **Парсинг Bus=** в `/proc/bus/input/devices`

### Возможности
- Python (production): GTK4, мультитач, AT-SPI авто-показ, обучение, оверлей
- C++ (experimental): touchflowd-cpp, AppImage
- Удаление: uninstall.sh, TouchFlow-Uninstall AppImage
- `scripts/fresh-install.sh` — переустановка с нуля
