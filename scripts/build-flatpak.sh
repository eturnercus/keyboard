#!/bin/bash
set -e
# Публикация в Flathub (локальная сборка)
cd "$(dirname "$0")/.."
flatpak-builder --user --install --force-clean build-dir flatpak/com.touchflow.Keyboard.yml
echo "✓ Flatpak установлен локально"
echo "  Для Flathub: fork flathub repo и submit PR с этим manifest"
