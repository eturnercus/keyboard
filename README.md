<p align="center">
  <img src="assets/logo.svg" alt="TouchFlow Logo" width="128" height="128">
</p>

<h1 align="center">TouchFlow Keyboard</h1>

<p align="center">
  <strong>Экранная клавиатура для сенсорного Linux</strong><br>
  Мультитач · RU/EN/UK/DE/FR · Обучение · Оверлей · KDE Wayland
</p>

<p align="center">
  <a href="https://github.com/eturnercus/keyboard/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version 1.0.0"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-green" alt="License GPL-3.0"></a>
  <a href="https://github.com/eturnercus/keyboard"><img src="https://img.shields.io/badge/platform-Linux-lightgrey" alt="Platform Linux"></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/lang-English-blue" alt="English README"></a>
</p>

<p align="center">
  <a href="https://github.com/eturnercus/keyboard">Репозиторий</a> ·
  <a href="https://github.com/eturnercus/keyboard/releases/tag/v1.0.0">Релизы</a> ·
  <a href="README.en.md">English README</a>
</p>

---

## Возможности

**TouchFlow** — экранная клавиатура для планшетов, киосков, панелей и 2-в-1 на Linux (Debian, Ubuntu, Fedora, Arch и др.).

### Клавиатура и ввод

- **Мультитач** — до 10 одновременных касаний
- **Авто-показ** при фокусе на поле ввода через AT-SPI
- **Движок обучения** — запоминает, где вы скрываете клавиатуру; порог показа и правила per-app (`auto`, `always_show`, `always_hide`)
- **Оверлей / gamepad** — полупрозрачный джойстик и кнопки (как на телефонах)
- **Языки:** русский, English, українська, Deutsch, Français (RU/EN/UK/DE/FR)
- **Быстрые действия:** копировать, вставить, вырезать, выделить всё, отмена, повтор, поиск (Ctrl+C/V/X/A/Z/Y/F)
- **F-клавиши** (F1–F12), **numpad**, **ряд стрелок**
- **Скрытие при внешней клавиатуре** (USB/BT)
- **Свайп снизу вверх** для показа клавиатуры

### Интеграция с системой

- **KDE Wayland** — виртуальная клавиатура (`X-KDE-Wayland-VirtualKeyboard`)
- **GNOME a11y** — экранная клавиатура через `gsettings`
- **Физические привязки** кнопок через evdev
- **D-Bus** API (`com.touchflow.Keyboard`) и **CLI** (`touchflow-cli`)

### Установка и сопровождение

- **Первый запуск** — пошаговое onboarding (6 шагов, один раз)
- **Правила обучения per-app** в настройках и `config.toml`
- **Python 1.0.0** — production-версия с полным GUI настроек
- **C++ 1.0.0** — экспериментальная нативная сборка (GTK4, без Python в рантайме)
- **`touchflow-doctor`** — диагностика установки (PATH, бинарники, systemd, uinput, KDE desktop)
- **AppImage-установщики:** Install Python, Install C++, Uninstall

---

## Быстрый старт

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-1.0.0.sh -o install-touchflow.sh
chmod +x install-touchflow.sh
./install-touchflow.sh
```

Перелогиньтесь для группы `input`, затем откройте **Настройки** → `touchflow-settings` или выберите TouchFlow в KDE.

---

## Установка

> **Скачать готовые сборки:** https://github.com/eturnercus/keyboard/releases/tag/v1.0.0

### Python AppImage (рекомендуется)

```bash
# x86_64
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Keyboard-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Keyboard-1.0.0-x86_64.AppImage
./TouchFlow-Keyboard-1.0.0-x86_64.AppImage
```

Для **aarch64** замените имя файла на `TouchFlow-Keyboard-1.0.0-aarch64.AppImage`. Откроется графический установщик — нажмите «Установить».

### Python shell-установщик (curl)

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-1.0.0.sh | bash
```

Работает на любой архитектуре; ставит зависимости, pip-пакет, systemd и desktop-файлы.

### Из git (`./scripts/install.sh`)

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
./scripts/install.sh
```

### C++ AppImage (экспериментальная)

```bash
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
./TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
```

### C++ shell-установщик (`install-cpp`)

```bash
curl -fsSL https://github.com/eturnercus/keyboard/releases/download/v1.0.0/touchflow-install-cpp-1.0.0.sh | bash
```

Или из исходников: `./scripts/install-cpp.sh`

### Требования

| Компонент | Назначение |
|-----------|------------|
| Группа **`input`** | Доступ к `/dev/uinput` для ввода клавиш |
| **Wayland** (KDE) | Виртуальная клавиатура в списке KDE — только Wayland, не X11 |
| GTK4, AT-SPI | Интерфейс и авто-показ при фокусе |
| `python3-evdev` | Обнаружение внешней клавиатуры (Python) |

**Debian/Ubuntu (Python):**

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-atspi-2.0 python3-evdev at-spi2-core
```

**Debian/Ubuntu (C++):**

```bash
sudo apt install build-essential cmake pkg-config g++ \
  libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev at-spi2-core
```

---

## После установки

```bash
touchflow-doctor                              # диагностика
touchflow-settings                            # настройки (полный путь: ~/.local/bin/touchflow-settings)
systemctl --user status touchflow-daemon      # статус демона Python
systemctl --user restart touchflow-daemon     # перезапуск
journalctl --user -u touchflow-daemon -e      # логи
```

Для C++: `systemctl --user status touchflow-daemon-cpp`

Если `touchflow-settings` не найден — проверьте `echo $PATH` (нужен `~/.local/bin`) или запустите `touchflow-doctor`.

**Перелогиньтесь** после установки (`sudo usermod -aG input $USER`).

---

## Настройки

| Команда | Версия | Описание |
|---------|--------|----------|
| `touchflow-settings` | Python (production) | Полный GUI: 10 разделов (Libadwaita) |
| `touchflow-settings-cpp` | C++ (experimental) | Упрощённые настройки C++ |

**Разделы `touchflow-settings`:**

| Раздел | Содержание |
|--------|------------|
| Поведение | Авто-показ, свайп, мультитач, внешняя клавиатура |
| Языки | RU, EN, UK, DE, FR; язык по умолчанию |
| Обучение | Порог, правила per-app, история, сброс |
| Раскладка | Высота, F-ряд, numpad, быстрые кнопки |
| Шрифты | Семейство, размер |
| Цвета | 6 цветов темы |
| Оверлей | Джойстик, прозрачность, позиции |
| Кнопки | Физические привязки evdev |
| Экран входа | Greeter (до логина) |
| О программе | Сброс, повтор onboarding |

Конфиг Python: `~/.config/touchflow/config.toml` — пример в [docs/config.example.toml](docs/config.example.toml).

Конфиг C++: `~/.config/touchflow/config-cpp.toml`

---

## KDE Virtual Keyboard (только Wayland)

1. Убедитесь, что сессия **Wayland** (не X11): `echo $XDG_SESSION_TYPE`
2. Установите TouchFlow (`./scripts/install.sh` или AppImage Python)
3. **Перелогиньтесь** (группа `input`)
4. Откройте **Параметры системы** → **Устройства ввода** → **Виртуальная клавиатура**
5. Выберите **TouchFlow** (или **TouchFlow C++** для C++-версии)
6. Если TouchFlow нет в списке:
   ```bash
   touchflow-doctor
   kbuildsycoca6 --noincremental   # или kbuildsycoca5
   ```
7. Перезапустите сессию KDE

> Не запускайте Python и C++ демоны одновременно. В KDE выберите **одну** виртуальную клавиатуру.

---

## Удаление

### Скрипт `uninstall.sh`

```bash
./scripts/uninstall.sh                        # с подтверждением
./scripts/uninstall.sh -y                       # без вопросов
./scripts/uninstall.sh -y --purge-config        # + ~/.config/touchflow
```

### AppImage удаления

```bash
curl -fsSL -O https://github.com/eturnercus/keyboard/releases/download/v1.0.0/TouchFlow-Uninstall-1.0.0-x86_64.AppImage
chmod +x TouchFlow-Uninstall-1.0.0-x86_64.AppImage
./TouchFlow-Uninstall-1.0.0-x86_64.AppImage
```

Удаляет Python и C++ компоненты (демоны, systemd, desktop, pip).

### `make uninstall`

```bash
make uninstall   # вызывает scripts/uninstall.sh -y
```

---

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| **`touchflow-settings` не найден** | `echo $PATH` — добавьте `~/.local/bin`; перелогиньтесь; запустите `touchflow-doctor` |
| **`touchflow-doctor` показывает ошибки** | Переустановите: `./scripts/install.sh`; проверьте `~/.local/bin/touchflow-settings` |
| **`TypeError: pressed` в journalctl** | Обновите до **1.0.0** — исправлен сигнал GTK4 (`clicked` вместо `pressed`) |
| **`uinput init failed` / клавиши не вводятся** | `sudo usermod -aG input $USER` и **перелогин** |
| **TouchFlow не в списке виртуальных клавиатур (KDE)** | Только **Wayland**; `./scripts/install.sh`; **Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow**; `kbuildsycoca6 --noincremental` |
| **AppImage — ничего не происходит** | `sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 zenity` |
| **Демон не работает** | `systemctl --user status touchflow-daemon` и `journalctl --user -u touchflow-daemon -e` |
| **Не появляется при фокусе** | `at-spi2-core`; `export GTK_MODULES=gail:atk-bridge` |
| **Не скрывается при USB-клавиатуре** | Настройки → Поведение → «Скрывать при внешней клавиатуре» |
| **Обучение мешает** | Настройки → Обучение → правило `always_show` или сброс |

---

## C++ 1.0.0 (экспериментальная)

Нативный демон **`touchflowd-cpp`** — C++20 + GTK4 + libadwaita. Статус: **experimental**; для продакшена используйте Python.

| | Python 1.0.0 | C++ 1.0.0 |
|---|--------------|-----------|
| Статус | **Production** | **Experimental** |
| Демон | `touchflowd` | `touchflowd-cpp` |
| Настройки | `touchflow-settings` (GUI) | `touchflow-settings-cpp` |
| systemd | `touchflow-daemon.service` | `touchflow-daemon-cpp.service` |
| Языки | RU/EN/UK/DE/FR | RU/EN |
| Обучение | Полное + per-app | Базовое (порог) |
| Оверлей / gamepad | Да | Нет |
| Установка | AppImage / `install.sh` / curl | AppImage C++ / `install-cpp.sh` |
| Конфиг | `config.toml` | `config-cpp.toml` |

Подробности: [`experimental/touchflow-cpp/README.md`](experimental/touchflow-cpp/README.md)

```bash
touchflowd-cpp                    # обычный режим
touchflowd-cpp --virtual-keyboard # режим KDE/GNOME виртуальной клавиатуры
```

---

## CLI и D-Bus

**D-Bus:** `com.touchflow.Keyboard` на `/com/touchflow/Keyboard`

| Команда | Действие |
|---------|----------|
| `touchflow-cli show` | Показать клавиатуру |
| `touchflow-cli hide` | Скрыть клавиатуру |
| `touchflow-cli toggle` | Показать/скрыть |
| `touchflow-cli overlay` | Переключить оверлей (gamepad) |
| `touchflow-cli reload` | Перезагрузить конфиг |
| `touchflow-cli reset-learning` | Сбросить данные обучения |

Демон должен быть запущен (`systemctl --user status touchflow-daemon`).

---

## Разработка

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
pip install -e ".[dev]"

make test           # pytest (tests/)
make lint           # ruff
make appimage       # dist/TouchFlow-Keyboard-1.0.0-x86_64.AppImage
make appimage-cpp   # dist/TouchFlow-Keyboard-Cpp-1.0.0-x86_64.AppImage
make appimage-all   # Python + C++ + Uninstall AppImages
make release        # wheel + tar.gz в dist/
```

---

## Лицензия

[GPL-3.0-or-later](LICENSE) — TouchFlow Keyboard © TouchFlow Contributors
