#!/usr/bin/env bash
# Обёртка для запуска touchflowd — находит бинарник в PATH
set -euo pipefail

find_touchflowd() {
    if command -v touchflowd &>/dev/null; then
        command -v touchflowd
        return
    fi
    for p in "$HOME/.local/bin/touchflowd" "/usr/local/bin/touchflowd" "/usr/bin/touchflowd"; do
        if [[ -x "$p" ]]; then
            echo "$p"
            return
        fi
    done
    return 1
}

BIN=$(find_touchflowd) || {
    echo "touchflowd не найден. Запустите установщик или: ./scripts/install.sh" >&2
    if command -v zenity &>/dev/null; then
        zenity --error --text="TouchFlow не установлен.\nЗапустите установщик или:\ncurl -fsSL .../touchflow-install.sh | bash"
    fi
    exit 127
}

export GTK_MODULES="${GTK_MODULES:-}gail:atk-bridge"
export QT_ACCESSIBILITY=1

exec "$BIN" "$@"
