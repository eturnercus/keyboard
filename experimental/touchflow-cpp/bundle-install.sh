#!/usr/bin/env bash
# Установка TouchFlow C++ из AppImage / bundle
set -euo pipefail

BUNDLE_ROOT="${TOUCHFLOW_CPP_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
BIN_SRC="${BUNDLE_ROOT}/usr/bin/touchflowd-cpp"
SETTINGS_SRC="${BUNDLE_ROOT}/usr/bin/touchflow-settings-cpp"
DATA_DIR="${BUNDLE_ROOT}/usr/share/touchflow-cpp/data"
VERSION="${TOUCHFLOW_CPP_VERSION:-1.0.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/lib/cpp-integration.sh
source "${BUNDLE_ROOT}/usr/share/touchflow-cpp/cpp-integration.sh" 2>/dev/null \
    || source "$(dirname "$SCRIPT_DIR")/../../scripts/lib/cpp-integration.sh" 2>/dev/null \
    || true

log() { echo "[touchflow-cpp] $*"; }

install_runtime_deps() {
    if command -v apt-get &>/dev/null; then
        log "Установка runtime-зависимостей (apt)..."
        sudo apt-get update -qq
        sudo apt-get install -y \
            libgtk-4-1 libadwaita-1-0 libevdev2 at-spi2-core dbus-x11
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y gtk4 libadwaita libevdev at-spi2-core
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --needed gtk4 libadwaita libevdev at-spi2-core
    fi
}

install_binary_and_desktop() {
    local home_bin="${HOME}/.local/bin"
    local apps="${HOME}/.local/share/applications"
    mkdir -p "$home_bin" "$apps"

    [[ -x "$BIN_SRC" ]] || { echo "Ошибка: нет $BIN_SRC" >&2; exit 1; }
    cp "$BIN_SRC" "$home_bin/touchflowd-cpp"
    chmod +x "$home_bin/touchflowd-cpp"
    if [[ -x "$SETTINGS_SRC" ]]; then
        cp "$SETTINGS_SRC" "$home_bin/touchflow-settings-cpp"
        chmod +x "$home_bin/touchflow-settings-cpp"
    fi

    for f in "$DATA_DIR"/*.desktop; do
        [[ -f "$f" ]] || continue
        local name base
        name=$(basename "$f")
        case "$name" in
            com.touchflow.Keyboard.Virtual.desktop)
                sed "s|Exec=touchflowd-cpp|Exec=${home_bin}/touchflowd-cpp --virtual-keyboard|g" "$f" > "$apps/$name"
                ;;
            com.touchflow.Settings.Cpp.desktop)
                sed "s|Exec=touchflow-settings-cpp|Exec=${home_bin}/touchflow-settings-cpp|g" "$f" > "$apps/$name"
                ;;
            *)
                sed "s|Exec=touchflowd-cpp|Exec=${home_bin}/touchflowd-cpp|g" "$f" > "$apps/$name"
                ;;
        esac
    done

    if [[ -f "${BUNDLE_ROOT}/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg" ]]; then
        local icons="${HOME}/.local/share/icons/hicolor/scalable/apps"
        mkdir -p "$icons"
        cp "${BUNDLE_ROOT}/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg" \
            "$icons/com.touchflow.Keyboard.svg"
    fi
}

post_install() {
    if declare -f install_cpp_systemd &>/dev/null; then
        install_cpp_systemd
        register_kde_cpp
    fi
    sudo usermod -aG input "${USER}" 2>/dev/null || true
    update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
    for cmd in kbuildsycoca6 kbuildsycoca5; do
        command -v "$cmd" &>/dev/null && "$cmd" --noincremental 2>/dev/null && break
    done
}

main() {
    log "TouchFlow C++ ${VERSION} (experimental)"
    install_runtime_deps
    install_binary_and_desktop
    post_install
    echo ""
    echo "✓ touchflowd-cpp установлен!"
    echo "  Настройки: touchflow-settings-cpp"
    echo "  Демон: systemctl --user status touchflow-daemon-cpp"
    echo "  Перелогиньтесь для группы input."
}

main "$@"
