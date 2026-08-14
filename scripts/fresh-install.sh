#!/usr/bin/env bash
# TouchFlow — полная переустановка с нуля (без sudo для systemctl --user)
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
REPO="${TOUCHFLOW_REPO:-https://github.com/eturnercus/keyboard}"
VERSION="${TOUCHFLOW_VERSION:-1.0.0}"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "==> TouchFlow Fresh Install v${VERSION}"
echo "    Пользователь: ${USER}"
echo "    Архитектура: $(uname -m)"

echo "==> Скачивание исходников..."
curl -fsSL "${REPO}/archive/refs/tags/v${VERSION}.tar.gz" -o "$TMP/src.tar.gz"
tar -xzf "$TMP/src.tar.gz" -C "$TMP"
SRC="$TMP/keyboard-${VERSION}"
if [[ ! -d "$SRC" ]]; then
    SRC="$TMP/keyboard-main"
fi

echo "==> Удаление старой установки..."
if [[ -f "$SRC/scripts/uninstall.sh" ]]; then
    bash "$SRC/scripts/uninstall.sh" -y
else
    curl -fsSL "${REPO}/releases/download/v${VERSION}/touchflow-install-${VERSION}.sh" -o "$TMP/old-install.sh" || true
fi

echo "==> Установка TouchFlow ${VERSION}..."
bash "$SRC/scripts/install.sh"

echo "==> Запуск демона (без sudo)..."
systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable --now touchflow-daemon 2>/dev/null || true
systemctl --user restart touchflow-daemon 2>/dev/null || true

sleep 2
if command -v touchflow-doctor &>/dev/null; then
    touchflow-doctor || true
fi

echo ""
echo "✓ Переустановка завершена!"
echo "  Показать клавиатуру: touchflow-cli show"
echo "  Настройки: touchflow-settings"
echo ""
echo "  Если демон не запустился — БЕЗ sudo:"
echo "    systemctl --user status touchflow-daemon"
echo "    journalctl --user -u touchflow-daemon -e"
