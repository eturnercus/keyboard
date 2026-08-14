#!/bin/bash
set -e
# Сборка .deb пакета
cd "$(dirname "$0")/.."
dpkg-buildpackage -us -uc -b
echo "✓ .deb создан в ../"
