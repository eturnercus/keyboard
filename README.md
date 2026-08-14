<p align="center">
  <img src="assets/logo.svg" alt="TouchFlow Logo" width="128" height="128">
</p>

<h1 align="center">TouchFlow Keyboard</h1>

<p align="center">
  <strong>Надёжная экранная клавиатура для Linux</strong><br>
  Мультитач · Авто-показ · Обучение · Оверлей-джойстик · Работа до входа в систему
</p>

<p align="center">
  <a href="#установка">Установка</a> ·
  <a href="#возможности">Возможности</a> ·
  <a href="#настройка">Настройка</a> ·
  <a href="#сборка">Сборка</a> ·
  <a href="#архитектура">Архитектура</a>
</p>

---

## О проекте

**TouchFlow** — экранная клавиатура для сенсорных Linux-устройств (планшеты, киоски, панели, 2-в-1 ноутбуки). Работает на Debian, Ubuntu, Fedora, Arch и других дистрибутивах с GTK4.

### Почему TouchFlow?

| Проблема | Решение TouchFlow |
|----------|-------------------|
| Клавиатура мешает когда подключена USB/BT клавиатура | Авто-скрытие при подключении внешней клавиатуры |
| Не появляется при нажатии на поле ввода | AT-SPI авто-показ при фокусе текстового поля |
| Появляется когда не нужна | Обучение запоминает ваши привычки |
| Нет F-клавиш и стрелок | Полный набор: F1–F12, цифры, стрелки, numpad |
| Нужен геймпад на экране | Режим оверлея с джойстиком и настраиваемыми кнопками |
| Не работает на экране входа | systemd-сервис для GDM/LightDM/SDDM |

---

## Возможности

### Клавиатура
- **Мультитач** — до 10 одновременных нажатий
- **Раскладки** RU/EN с переключением одной кнопкой
- **F1–F12**, цифровой ряд, стрелки, numpad (опционально)
- **Модификаторы**: Shift, Ctrl, Alt, Caps Lock
- **Свайп снизу** — проведите пальцем снизу вверх для показа

### Умное поведение
- **Авто-показ** при фокусе на поле ввода (через AT-SPI)
- **Авто-скрытие** при потере фокуса
- **Обучение** — запоминает приложения, где вы сразу скрываете клавиатуру
- **Внешняя клавиатура** — скрывается при подключении USB/BT клавиатуры, появляется при отключении

### Оверлей (режим как на телефонах)
- Полупрозрачный **джойстик** для навигации
- Настраиваемые **кнопки** (A/B/X/Y, L1/R1 и любые другие)
- Перетаскивание и изменение размера в режиме редактирования
- Привязка к любым клавишам

### Физические кнопки
- Привязка любых клавиш evdev к действиям (показать/скрыть/переключить оверлей)
- По умолчанию: F23 для переключения видимости

### Экран входа (Greeter)
- Работа **до входа в систему** на GDM, LightDM, SDDM
- Отдельный systemd-сервис

### Настройки
- Отдельное приложение **TouchFlow Settings** (GTK4/Libadwaita)
- Цвета, размеры, шрифты, поведение, оверлей — всё настраивается
- Конфиг в TOML для продвинутых пользователей
- D-Bus API и CLI

---

## Установка

### Быстрая установка (Debian/Ubuntu)

```bash
git clone https://github.com/touchflow/touchflow-keyboard.git
cd touchflow-keyboard
chmod +x scripts/install.sh
./scripts/install.sh
```

После установки перелогиньтесь (для группы `input`).

### Зависимости

**Debian/Ubuntu:**
```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
  gir1.2-atspi-2.0 python3-evdev at-spi2-core dbus-x11
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4 libadwaita at-spi2-core python3-evdev
```

**Arch:**
```bash
sudo pacman -S python python-gobject gtk4 libadwaita at-spi2-core python-evdev
```

**Опционально** (для Wayland layer-shell):
```bash
# gtk4-layer-shell — улучшенное позиционирование поверх всех окон
```

### Экран входа (до логина)

```bash
sudo ./scripts/install-greeter.sh
sudo systemctl restart gdm   # или lightdm / sddm
```

### Запуск

```bash
# Демон (обычно стартует автоматически через systemd)
touchflowd

# Настройки
touchflow-settings

# CLI
touchflow-cli show
touchflow-cli hide
touchflow-cli toggle
touchflow-cli overlay
touchflow-cli reset-learning
```

---

## Настройка

### Графический интерфейс

Запустите `touchflow-settings`. Разделы:

| Раздел | Что настраивается |
|--------|-------------------|
| **Поведение** | Авто-показ, свайп, обучение, внешняя клавиатура, мультитач |
| **Раскладка** | Высота, ширина, ряды F/цифр/стрелок, numpad |
| **Цвета** | Фон, клавиши, нажатие, текст, акцент |
| **Оверлей** | Джойстик, кнопки, прозрачность |
| **Экран входа** | Работа до логина |
| **О программе** | Сброс обучения и настроек |

### Файл конфигурации

Путь: `~/.config/touchflow/config.toml`

Пример: [docs/config.example.toml](docs/config.example.toml)

#### Ключевые параметры

```toml
[behavior]
auto_show = true                          # Показ при фокусе на поле ввода
hide_on_external_keyboard = true            # Скрывать при USB/BT клавиатуре
show_on_external_keyboard_disconnect = true
swipe_from_bottom = true                    # Свайп снизу
learning_enabled = true                     # Обучение

[layout]
height_px = 280                             # Высота клавиатуры
show_function_row = true                    # F1-F12
show_number_row = true
show_arrow_row = true
show_numpad = false

[bindings]
toggle_visibility = ["KEY_F23"]             # Физическая кнопка
```

#### Оверлей — кнопки

```toml
[[overlay.buttons]]
id = "btn_a"
label = "A"
x_percent = 85.0
y_percent = 75.0
width_px = 64
height_px = 64
opacity = 0.55
action = "key"
payload = "KEY_A"
shape = "circle"   # circle | rect | diamond
```

### D-Bus API

Шина: `com.touchflow.Keyboard`, путь: `/com/touchflow/Keyboard`

```bash
dbus-send --session --dest=com.touchflow.Keyboard \
  /com/touchflow/Keyboard com.touchflow.Keyboard1.Show
```

Методы: `Show`, `Hide`, `Toggle`, `ReloadConfig`, `ResetLearning`, `ToggleOverlay`, `SetOverlayEditMode`

---

## Сборка

### Из исходников

```bash
# Установка зависимостей для разработки
pip install -e ".[dev]"

# Тесты
make test

# Линтер
make lint

# Релиз
make release
# Артефакты в dist/
```

### Релиз

```bash
./scripts/build-release.sh
```

Создаёт:
- `dist/touchflow_keyboard-1.0.0-py3-none-any.whl`
- `dist/touchflow-keyboard-1.0.0.tar.gz`
- `dist/touchflow-keyboard-1.0.0-linux.tar.gz`

---

## Архитектура

```
touchflow/
├── daemon.py           # Главный демон (GTK4)
├── keyboard_widget.py  # Виджет клавиатуры + мультитач
├── overlay.py          # Оверлей с джойстиком
├── gestures.py         # Свайп снизу
├── focus_watcher.py    # AT-SPI авто-показ
├── external_kb.py      # Детекция внешней клавиатуры
├── learning.py         # Обучение показа/скрытия
├── key_inject.py       # Ввод через uinput
├── physical_bindings.py# Физические кнопки
├── config.py           # TOML конфигурация
└── dbus_iface.py       # D-Bus API

touchflow_settings/
└── app.py              # Приложение настроек (Libadwaita)
```

### Как это работает

```
┌─────────────────────────────────────────────────────────┐
│                    TouchFlow Daemon                      │
├─────────────┬──────────────┬──────────────┬─────────────┤
│  AT-SPI     │  /proc/bus/  │   Learning   │   uinput    │
│  Focus      │  input       │   Engine     │   Inject    │
│  Watcher    │  (ext. KB)   │              │             │
└──────┬──────┴──────┬───────┴──────┬───────┴──────┬──────┘
       │             │              │              │
       ▼             ▼              ▼              ▼
  Авто-показ    Скрыть при      Запомнить     Отправить
  при фокусе    USB клавиатуре  привычки      нажатия
```

### Надёжность

- **Автоперезапуск** через systemd (`Restart=on-failure`)
- **Атомарная запись** конфига и данных обучения (`.tmp` + rename)
- **Graceful degradation**: без AT-SPI — ручной показ; без uinput — предупреждение; без layer-shell — обычное окно
- **Нет зависимости от X11/Wayland** для ввода (uinput работает везде)
- **Минимум внешних зависимостей**: Python, GTK4, evdev

---

## Устранение неполадок

| Симптом | Решение |
|---------|---------|
| Клавиатура не появляется при фокусе | Проверьте `at-spi2-core`, переменные `GTK_MODULES=gail:atk-bridge` |
| Клавиши не вводятся | Добавьте пользователя в группу `input`: `sudo usermod -aG input $USER` |
| Не скрывается при USB клавиатуре | Убедитесь что `hide_on_external_keyboard = true` |
| Не работает на экране входа | Запустите `sudo ./scripts/install-greeter.sh` |
| Демон не стартует | `journalctl --user -u touchflow-daemon -f` |

---

## Лицензия

GPL-3.0-or-later — см. [LICENSE](LICENSE)

---

<p align="center">
  Сделано для сенсорного Linux · Просто · Надёжно · Настраиваемо
</p>
