# TouchFlow C++ 1.0.0 (экспериментальная)

Нативная переписка TouchFlow на **C++20 + GTK4 + libadwaita**.

> **Статус:** экспериментальная сборка 1.0.0. Основная (production) версия — Python в корне репозитория.

## Возможности (C++ 1.0.0)

- GTK4 клавиатура: RU/EN раскладки, F-ряд, цифры, стрелки
- Быстрые действия: копировать, вставить, вырезать, выделить всё, отмена, повтор
- uinput/evdev ввод клавиш
- AT-SPI авто-показ при фокусе на текстовом поле
- Обнаружение внешней клавиатуры
- Простое обучение (порог показа)
- KDE virtual keyboard desktop (`--virtual-keyboard`)

## Установка

### AppImage (рекомендуется)

```bash
# Из Releases: TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Keyboard-Cpp-*.AppImage
./TouchFlow-Keyboard-Cpp-*.AppImage
```

### Shell / исходники

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/latest/download/touchflow-install-cpp-1.0.0.sh | bash
# или
./scripts/install-cpp.sh
```

## Сборка

```bash
sudo apt install build-essential cmake pkg-config \
  libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev at-spi2-core

cd experimental/touchflow-cpp
CXX=g++ cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/touchflowd-cpp --version
```

Сборка AppImage-установщика:

```bash
make appimage-cpp
# → dist/TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
```

## Установка

```bash
./scripts/install-cpp.sh
```

## Структура

```
src/
  main.cpp           — точка входа
  daemon.cpp         — демон, авто-показ, внешняя KB
  keyboard_view.cpp  — виджет клавиатуры
  key_injector.cpp   — uinput
  focus_watcher.cpp  — AT-SPI
  external_kb.cpp    — /proc/bus/input/devices
  learning.cpp       — обучение
  config.cpp         — config-cpp.toml
  layouts.cpp        — RU/EN раскладки
data/
  com.touchflow.Keyboard.Virtual.desktop
```

Конфиг: `~/.config/touchflow/config-cpp.toml`

## Связь с Python 1.0.0

| | Python | C++ |
|---|--------|-----|
| Версия | 1.0.0 (production) | 1.0.0 (experimental) |
| Бинарник | touchflowd | touchflowd-cpp |
| Настройки | touchflow-settings | config-cpp.toml |
| Языки | RU/EN/UK/DE/FR | RU/EN |
