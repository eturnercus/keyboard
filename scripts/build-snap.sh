#!/bin/bash
set -e
# Сборка Snap
cd "$(dirname "$0")/.."
snapcraft --use-lxd
echo "✓ Snap собран"
echo "  snap install --dangerous touchflow-keyboard_*.snap"
