#!/usr/bin/env bash
# TouchFlow — установка на Debian/Ubuntu и совместимые дистрибутивы
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> TouchFlow Keyboard Installer"

if command -v apt-get &>/dev/null; then
    echo "==> Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-4.0 \
        gir1.2-adw-1 gir1.2-atspi-2.0 python3-evdev at-spi2-core dbus-x11 \
        zenity 2>/dev/null || true
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3-gobject gtk4 libadwaita at-spi2-core python3-evdev zenity
elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed python python-gobject gtk4 libadwaita at-spi2-core python-evdev zenity
fi

echo "==> Installing Python package..."
python3 -m pip install --user "$ROOT" 2>/dev/null \
    || python3 -m pip install --user --break-system-packages "$ROOT"

echo "==> System integration (KDE, GNOME, systemd)..."
python3 -c "
from pathlib import Path
from touchflow.system_integration import full_system_register
print(full_system_register(Path('$ROOT')))
"

echo "==> Adding user to input group..."
sudo usermod -aG input "$USER" 2>/dev/null || true

# Обновить кэш desktop
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo ""
echo "✓ TouchFlow установлен!"
echo "  KDE: Параметры системы → Устройства ввода → Виртуальная клавиатура → TouchFlow"
echo "  Настройки: touchflow-settings"
echo "  Проверка: systemctl --user status touchflow-daemon"
echo "  Перелогиньтесь для группы input."
