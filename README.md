<p align="center">
  <img src="assets/logo.svg" alt="TouchFlow Logo" width="128" height="128">
</p>

<h1 align="center">TouchFlow Keyboard</h1>

<p align="center">
  <strong>Экранная клавиатура для сенсорного Linux</strong><br>
  Мультитач · RU/EN · Обучение · Оверлей · До входа в систему
</p>

---

## Что это

**TouchFlow** — экранная клавиатура для планшетов, киосков, панелей и 2-в-1 на Linux (Debian, Ubuntu, Fedora, Arch и др.).

При первом запуске показывается короткое обучение (один раз). Дальше — только если нажать «Показать обучение снова» в настройках.

## Установка

> **Скачать готовые сборки:** https://github.com/eturnercus/keyboard/releases

### AppImage (рекомендуется)

```bash
# Скачайте из Releases, затем:
chmod +x TouchFlow-Keyboard-1.0.2-x86_64.AppImage
./TouchFlow-Keyboard-1.0.2-x86_64.AppImage
```

> **ARM (aarch64)?** Скачайте `TouchFlow-Keyboard-*-aarch64.AppImage` или используйте shell-установщик:
> ```bash
> curl -fsSL https://github.com/eturnercus/keyboard/releases/latest/download/touchflow-install-1.0.2.sh | bash
> ```

> **Ошибка «формат выполняемого файла»?** Вы скачали x86_64 на ARM (или наоборот). Проверьте: `uname -m`

Откроется графический установщик — нажмите «Установить».

### Из исходников

```bash
git clone https://github.com/eturnercus/keyboard.git
cd keyboard
./scripts/install.sh
```

Перелогиньтесь для группы `input`.

### AppImage (установщик в один клик)

```bash
make appimage
# → dist/TouchFlow-Keyboard-1.0.1-x86_64.AppImage

chmod +x dist/TouchFlow-Keyboard-*.AppImage
./dist/TouchFlow-Keyboard-*.AppImage
```

AppImage откроет графический установщик: поставит зависимости, touchflowd, systemd и desktop-файлы.

### Быстрые кнопки

На клавиатуре есть ряд быстрых действий:

| Кнопка | Действие |
|--------|----------|
| Копир. | Ctrl+C |
| Встав. | Ctrl+V |
| Вырез. | Ctrl+X |
| Всё | Ctrl+A (выделить всё) |
| Отмена | Ctrl+Z |
| Повт. | Ctrl+Y |
| Поиск | Ctrl+F |

Включить/выключить: **Настройки → Раскладка → Быстрые кнопки**

### Магазины Linux

| Платформа | Команда |
|-----------|---------|
| **Flathub** | `flatpak install flathub com.touchflow.Keyboard` *(после публикации)* |
| **Snap Store** | `snap install touchflow-keyboard` *(после публикации)* |
| **.deb (Debian/Ubuntu)** | `sudo apt install ./touchflow-keyboard_1.0.0_all.deb` |

Локальная сборка пакетов:

```bash
./scripts/build-flatpak.sh   # Flatpak
./scripts/build-snap.sh      # Snap
./scripts/build-deb.sh       # .deb
make release                 # wheel + tar.gz
```

### Зависимости (если ставите вручную)

```bash
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-atspi-2.0 python3-evdev at-spi2-core

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita at-spi2-core python3-evdev

# Arch
sudo pacman -S python-gobject gtk4 libadwaita at-spi2-core python-evdev
```

## Запуск

```bash
touchflowd              # демон (автостарт через systemd)
touchflow-settings      # настройки
touchflow-cli toggle    # показать/скрыть
```

## Возможности (v1.0.0)

### Языки
- **Русский** и **English** по умолчанию
- Дополнительно: Українська, Deutsch, Français
- Включение/отключение языков в **Настройки → Языки**
- Кнопка 🌐 или RU/EN на клавиатуре для переключения

### Обучение
- Запоминает, где вы скрываете клавиатуру
- **Настройки → Обучение**:
  - Порог показа (0.0–1.0)
  - Правила per-app: `always_show`, `always_hide`, `auto`
  - История по приложениям
  - Сброс обучения

### Поведение
- Авто-показ при фокусе на поле ввода
- Скрытие при подключении USB/BT клавиатуры
- Свайп снизу вверх
- Мультитач (до 10 клавиш)
- F1–F12, стрелки, numpad

### Оверлей
- Полупрозрачный джойстик и кнопки (как на телефонах)
- Редактирование позиций в настройках

### Первый запуск
- Полупрозрачное окно с 6 шагами обучения
- Показывается **только один раз**
- Повтор: **Настройки → О программе → Показать обучение снова**

### Сброс
- **Сбросить обучение** — только данные обучения
- **Сбросить настройки** — config.toml (бэкап в .bak)
- **Полный сброс** — настройки + обучение + флаг первого запуска

### Экран входа
```bash
sudo ./scripts/install-greeter.sh
sudo systemctl restart gdm   # или lightdm / sddm
```

## Настройки

`touchflow-settings` — 10 разделов:

| Раздел | Содержание |
|--------|------------|
| Поведение | Авто-показ, свайп, мультитач, внешняя клавиатура |
| **Языки** | Вкл/выкл RU, EN, UK, DE, FR; язык по умолчанию |
| **Обучение** | Порог, правила per-app, история, сброс |
| Раскладка | Высота, F-ряд, numpad |
| Шрифты | Семейство, размер |
| Цвета | 6 цветов |
| Оверлей | Джойстик, прозрачность |
| Кнопки | Физические привязки evdev |
| Экран входа | Greeter |
| О программе | Сброс, обучение снова |

Конфиг: `~/.config/touchflow/config.toml` — пример в [docs/config.example.toml](docs/config.example.toml).

### Пример: правило обучения

```toml
[[learning.rules]]
app_id = "firefox"
window_class = ""
mode = "always_hide"   # auto | always_show | always_hide
```

### Пример: добавить язык

```toml
[[languages.entries]]
code = "uk"
name = "Українська"
enabled = true
is_default = false
```

## CLI и D-Bus

```bash
touchflow-cli show
touchflow-cli hide
touchflow-cli toggle
touchflow-cli overlay
touchflow-cli reset-learning
touchflow-cli reload
```

## Сборка и тесты

```bash
pip install -e ".[dev]"
make test      # 10 тестов
make release   # dist/
```

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| Не появляется при фокусе | `at-spi2-core`, `export GTK_MODULES=gail:atk-bridge` |
| Клавиши не вводятся | `sudo usermod -aG input $USER`, перелогин |
| Не скрывается при USB KB | Настройки → Поведение → «Скрывать при внешней клавиатуре» |
| Обучение мешает | Настройки → Обучение → правило `always_show` или сброс |
| Не работает до логина | `sudo ./scripts/install-greeter.sh` |

## Лицензия

GPL-3.0-or-later — [LICENSE](LICENSE)
