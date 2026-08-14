# TouchFlow C++ (экспериментальная ветка)

Нативная переписка TouchFlow на **C++20 + GTK4 + libadwaita**.

> Статус: **экспериментальный прототип**. Основная версия — Python в корне репозитория.

## Зачем

| Python (основная) | C++ (experimental) |
|-------------------|-------------------|
| Быстрая разработка | Меньше зависимостей в рантайме |
| pip + GTK | Один бинарник после сборки |
| AppImage тянет Python | Проще AppImage / .deb |

## Сборка

```bash
sudo apt install build-essential cmake pkg-config \
  libgtk-4-dev libadwaita-1-dev libevdev-dev

cd experimental/touchflow-cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/touchflowd
```

## Структура

```
src/
  main.cpp           — точка входа, GTK Application
  keyboard_window.*  — окно клавиатуры
  key_injector.*     — ввод через evdev/uinput
  config.*           — JSON/TOML конфиг (заглушка)
```

## Roadmap

- [x] Базовое окно с рядом клавиш
- [ ] Мультитач
- [ ] AT-SPI авто-показ
- [ ] KDE `X-KDE-Wayland-VirtualKeyboard`
- [ ] Паритет с Python-версией

## Связь с основным проектом

Конфиг совместим по пути: `~/.config/touchflow/config.toml` (планируется).
