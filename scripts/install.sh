#!/usr/bin/env bash
# TouchFlow — установка на Debian/Ubuntu и совместимые дистрибутивы
set -euo pipefail

PREFIX="${PREFIX:-/usr/local}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> TouchFlow Keyboard Installer"
echo "    Prefix: $PREFIX"

# Зависимости
if command -v apt-get &>/dev/null; then
    echo "==> Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-4.0 \
        gir1.2-adw-1 gir1.2-atspi-2.0 libgirepository1.0-dev \
        python3-evdev at-spi2-core dbus-x11 \
        2>/dev/null || true
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3-gobject gtk4 libadwaita at-spi2-core python3-evdev
elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed python python-gobject gtk4 libadwaita at-spi2-core python-evdev
fi

echo "==> Installing Python package..."
pip3 install --user "$ROOT" 2>/dev/null || sudo pip3 install "$ROOT"

BIN_DIR="$PREFIX/bin"
if [[ "$PREFIX" == "/usr/local" ]]; then
    BIN_DIR="$HOME/.local/bin"
fi

echo "==> Installing desktop files..."
mkdir -p "$HOME/.local/share/applications"
cp "$ROOT/data/com.touchflow.Settings.desktop" "$HOME/.local/share/applications/"
cp "$ROOT/data/com.touchflow.Keyboard.desktop" "$HOME/.local/share/applications/"

echo "==> Installing icon..."
mkdir -p "$HOME/.local/share/icons/hicolor/scalable/apps"
cp "$ROOT/assets/logo.svg" "$HOME/.local/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg"

echo "==> Installing systemd user service..."
mkdir -p "$HOME/.config/systemd/user"
cp "$ROOT/systemd/touchflow-daemon.service" "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable touchflow-daemon.service
systemctl --user start touchflow-daemon.service || true

echo "==> Adding user to input group (for uinput)..."
sudo usermod -aG input "$USER" 2>/dev/null || true

echo ""
echo "✓ TouchFlow установлен!"
echo "  Настройки: touchflow-settings"
echo "  CLI:       touchflow-cli show|hide|toggle"
echo ""
echo "  Перелогиньтесь для применения группы 'input'."
echo "  Для экрана входа: sudo $ROOT/scripts/install-greeter.sh"
