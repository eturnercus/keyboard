#!/usr/bin/env bash
# TouchFlow C++ (experimental) — установка
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CPP="$ROOT/experimental/touchflow-cpp"
# shellcheck source=lib/cpp-integration.sh
source "$SCRIPT_DIR/lib/cpp-integration.sh"

echo "==> TouchFlow C++ 1.0.0 (experimental)"

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y build-essential cmake pkg-config g++ \
        libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev at-spi2-core \
        libgtk-4-1 libadwaita-1-0 libevdev2 dbus-x11
fi

CXX=${CXX:-g++} cmake -S "$CPP" -B "$CPP/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$CPP/build" -j"$(nproc)"

BIN_DIR="$HOME/.local/bin"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$BIN_DIR" "$APPS" "$ICONS"

cp "$CPP/build/touchflowd-cpp" "$BIN_DIR/"
cp "$CPP/build/touchflow-settings-cpp" "$BIN_DIR/"
chmod +x "$BIN_DIR/touchflowd-cpp" "$BIN_DIR/touchflow-settings-cpp"

for f in "$CPP/data/"*.desktop; do
    name=$(basename "$f")
    case "$name" in
        com.touchflow.Keyboard.Virtual.desktop)
            sed "s|Exec=touchflowd-cpp|Exec=${BIN_DIR}/touchflowd-cpp --virtual-keyboard|g" "$f" > "$APPS/$name"
            ;;
        com.touchflow.Settings.Cpp.desktop)
            sed "s|Exec=touchflow-settings-cpp|Exec=${BIN_DIR}/touchflow-settings-cpp|g" "$f" > "$APPS/$name"
            ;;
        *)
            sed "s|Exec=touchflowd-cpp|Exec=${BIN_DIR}/touchflowd-cpp|g" "$f" > "$APPS/$name"
            ;;
    esac
done

cp "$ROOT/assets/logo.svg" "$ICONS/com.touchflow.Keyboard.svg" 2>/dev/null || true

install_cpp_systemd
register_kde_cpp
sudo usermod -aG input "$USER" 2>/dev/null || true
update-desktop-database "$APPS" 2>/dev/null || true
for cmd in kbuildsycoca6 kbuildsycoca5; do
    command -v "$cmd" &>/dev/null && "$cmd" --noincremental && break
done

echo ""
echo "✓ TouchFlow C++ установлен!"
echo "  Демон: systemctl --user status touchflow-daemon-cpp"
echo "  Настройки: touchflow-settings-cpp"
echo "  KDE: Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow"
echo "  Перелогиньтесь для группы input."
