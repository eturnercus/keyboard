#!/usr/bin/env bash
# Установка TouchFlow C++ из AppImage / bundle (без сборки на целевой машине)
set -euo pipefail

BUNDLE_ROOT="${TOUCHFLOW_CPP_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
BIN_SRC="${BUNDLE_ROOT}/usr/bin/touchflowd-cpp"
DATA_DIR="${BUNDLE_ROOT}/usr/share/touchflow-cpp/data"
VERSION="${TOUCHFLOW_CPP_VERSION:-1.0.0}"

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
    else
        log "Менеджер пакетов не найден — убедитесь, что установлены GTK4 и libevdev"
    fi
}

install_binary_and_desktop() {
    local home_bin="${HOME}/.local/bin"
    local apps="${HOME}/.local/share/applications"
    mkdir -p "$home_bin" "$apps"

    if [[ ! -x "$BIN_SRC" ]]; then
        echo "Ошибка: не найден бинарник touchflowd-cpp в $BIN_SRC" >&2
        exit 1
    fi

    log "Копирование touchflowd-cpp → $home_bin/"
    cp "$BIN_SRC" "$home_bin/touchflowd-cpp"
    chmod +x "$home_bin/touchflowd-cpp"

    log "Установка desktop-файлов..."
    for f in "$DATA_DIR"/*.desktop; do
        [[ -f "$f" ]] || continue
        local name
        name=$(basename "$f")
        sed "s|Exec=touchflowd-cpp|Exec=${home_bin}/touchflowd-cpp|g" "$f" > "$apps/$name"
    done

    if [[ -f "${BUNDLE_ROOT}/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg" ]]; then
        local icons="${HOME}/.local/share/icons/hicolor/scalable/apps"
        mkdir -p "$icons"
        cp "${BUNDLE_ROOT}/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg" \
            "$icons/com.touchflow.Keyboard.svg"
    fi
}

post_install() {
    sudo usermod -aG input "${USER}" 2>/dev/null || true

    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
    fi
    for cmd in kbuildsycoca6 kbuildsycoca5; do
        if command -v "$cmd" &>/dev/null; then
            "$cmd" --noincremental 2>/dev/null || true
            break
        fi
    done
}

main() {
    log "TouchFlow C++ ${VERSION} (experimental)"
    install_runtime_deps
    install_binary_and_desktop
    post_install
    log "Готово!"
    echo ""
    echo "✓ touchflowd-cpp установлен в ~/.local/bin/"
    echo "  Запуск: touchflowd-cpp"
    echo "  KDE Wayland: Параметры → Устройства ввода → Виртуальная клавиатура → TouchFlow"
    echo "  Перелогиньтесь для группы input."
}

main "$@"
