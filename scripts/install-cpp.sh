#!/usr/bin/env bash
# TouchFlow C++ (experimental) — установка
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CPP="$ROOT/experimental/touchflow-cpp"

echo "==> TouchFlow C++ 1.0.0 (experimental)"

if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y build-essential cmake pkg-config \
        libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev at-spi2-core
fi

cmake -S "$CPP" -B "$CPP/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$CPP/build" -j"$(nproc)"

mkdir -p "$HOME/.local/bin"
cp "$CPP/build/touchflowd-cpp" "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/touchflowd-cpp"

APPS="$HOME/.local/share/applications"
mkdir -p "$APPS"
cp "$CPP/data/"*.desktop "$APPS/"
sed -i "s|Exec=touchflowd-cpp|Exec=$HOME/.local/bin/touchflowd-cpp|g" "$APPS/com.touchflow.Keyboard."*.desktop

sudo usermod -aG input "$USER" 2>/dev/null || true
update-desktop-database "$APPS" 2>/dev/null || true
for cmd in kbuildsycoca6 kbuildsycoca5; do
    command -v "$cmd" &>/dev/null && "$cmd" --noincremental && break
done

echo ""
echo "✓ touchflowd-cpp установлен в ~/.local/bin/"
echo "  KDE: Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow"
echo "  Запуск: touchflowd-cpp"
echo "  Перелогиньтесь для группы input."
