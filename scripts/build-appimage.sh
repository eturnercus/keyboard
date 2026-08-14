#!/bin/bash
# Сборка установочного AppImage для TouchFlow Keyboard
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(python3 -c "from touchflow import __version__; print(__version__)")
ARCH=$(uname -m)
case "$ARCH" in
    x86_64|amd64)  APPIMAGE_ARCH="x86_64"; RUNTIME_NAME="runtime-x86_64" ;;
    aarch64|arm64) APPIMAGE_ARCH="aarch64"; RUNTIME_NAME="runtime-aarch64" ;;
    *) echo "Неподдерживаемая архитектура: $ARCH (нужен x86_64 или aarch64)"; exit 1 ;;
esac

APPDIR="$ROOT/build/TouchFlow-keyboard-${VERSION}-${APPIMAGE_ARCH}.AppDir"
OUTPUT="$ROOT/dist/TouchFlow-Keyboard-${VERSION}-${APPIMAGE_ARCH}.AppImage"
SQUASHFS="$ROOT/build/filesystem-${VERSION}.squashfs"
TOOLS="$ROOT/build/tools"
RUNTIME="$TOOLS/${RUNTIME_NAME}"

echo "==> TouchFlow AppImage Builder v${VERSION} (${APPIMAGE_ARCH})"

rm -rf "$APPDIR" "$SQUASHFS"
mkdir -p "$APPDIR/usr/share/touchflow" "$APPDIR/usr/bin" "$TOOLS" "$ROOT/dist"

# Копируем проект
tar -C "$ROOT" --exclude='./build' --exclude='./dist' --exclude='./.git' -cf - . \
    | tar -C "$APPDIR/usr/share/touchflow" -xf -

install -Dm644 "$ROOT/assets/logo.svg" "$APPDIR/touchflow-keyboard.svg"
install -Dm644 "$ROOT/assets/logo.svg" \
    "$APPDIR/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg"

cat > "$APPDIR/touchflow-keyboard.desktop" <<EOF
[Desktop Entry]
Name=TouchFlow Installer
Comment=Установить экранную клавиатуру TouchFlow
Exec=touchflow-installer
Icon=touchflow-keyboard
Type=Application
Categories=Utility;System;
Terminal=false
StartupNotify=true
EOF
install -Dm644 "$APPDIR/touchflow-keyboard.desktop" \
    "$APPDIR/usr/share/applications/touchflow-keyboard.desktop"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/share/touchflow:${PYTHONPATH:-}"
export PROJECT_ROOT="${HERE}/usr/share/touchflow"
export APPIMAGE="${APPIMAGE:-${0}}"
cd "${HERE}/usr/share/touchflow"
exec python3 -m touchflow.installer "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/usr/bin/touchflow-installer" <<'WRAPPER'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")/../../.."
export PYTHONPATH="${HERE}/usr/share/touchflow:${PYTHONPATH:-}"
export PROJECT_ROOT="${HERE}/usr/share/touchflow"
cd "${HERE}/usr/share/touchflow"
exec python3 -m touchflow.installer "$@"
WRAPPER
chmod +x "$APPDIR/usr/bin/touchflow-installer"

build_with_appimagetool() {
    local tool="$TOOLS/appimagetool-${APPIMAGE_ARCH}.AppImage"
    if [[ ! -f "$tool" ]]; then
        echo "==> Downloading appimagetool..."
        curl -fsSL -o "$tool" \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${APPIMAGE_ARCH}.AppImage"
        chmod +x "$tool"
    fi
    ARCH="$APPIMAGE_ARCH" "$tool" --appimage-extract-and-run "$APPDIR" "$OUTPUT" 2>/dev/null \
        || ARCH="$APPIMAGE_ARCH" "$tool" "$APPDIR" "$OUTPUT"
}

build_with_cat() {
    if [[ ! -f "$RUNTIME" ]]; then
        echo "==> Downloading AppImage runtime (${RUNTIME_NAME})..."
        curl -fsSL -o "$RUNTIME" \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/${RUNTIME_NAME}"
    fi
    echo "==> Creating squashfs..."
    mksquashfs "$APPDIR" "$SQUASHFS" -comp xz -noappend -no-progress
    echo "==> Assembling AppImage (runtime + squashfs)..."
    cat "$RUNTIME" "$SQUASHFS" > "$OUTPUT"
    chmod +x "$OUTPUT"
    rm -f "$SQUASHFS"
}

verify_appimage() {
    if ! file "$OUTPUT" | grep -q "ELF.*executable"; then
        echo "ERROR: AppImage не является исполняемым ELF-файлом!"
        file "$OUTPUT"
        exit 1
    fi
    echo "==> Verified: $(file -b "$OUTPUT")"
}

echo "==> Building AppImage..."
if command -v mksquashfs &>/dev/null; then
    build_with_cat
else
    sudo apt-get install -y squashfs-tools 2>/dev/null || true
    if command -v mksquashfs &>/dev/null; then
        build_with_cat
    else
        build_with_appimagetool
    fi
fi

verify_appimage

TAR_OUT="$ROOT/dist/TouchFlow-Keyboard-${VERSION}-${APPIMAGE_ARCH}.tar.gz"
tar -czf "$TAR_OUT" -C "$ROOT/build" "$(basename "$APPDIR")"

# Универсальный shell-установщик (работает на любой архитектуре)
INSTALLER_SH="$ROOT/dist/touchflow-install-${VERSION}.sh"
cat > "$INSTALLER_SH" <<HEADER
#!/bin/bash
# TouchFlow Keyboard — универсальный установщик (любая архитектура)
set -euo pipefail
REPO="https://github.com/eturnercus/keyboard"
TMP=\$(mktemp -d)
trap 'rm -rf "\$TMP"' EXIT

echo "==> TouchFlow Keyboard Installer v${VERSION}"
echo "    Архитектура: \$(uname -m)"

if ! command -v python3 &>/dev/null; then
    echo "Ошибка: нужен python3. Установите: sudo apt install python3"
    exit 1
fi

echo "==> Скачивание..."
curl -fsSL "\${REPO}/archive/refs/heads/main.tar.gz" -o "\$TMP/src.tar.gz"
tar -xzf "\$TMP/src.tar.gz" -C "\$TMP"
SRC="\$TMP/keyboard-main"

echo "==> Установка зависимостей (может запросить sudo)..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \\
        gir1.2-atspi-2.0 python3-evdev at-spi2-core python3-pip dbus-x11
elif command -v dnf &>/dev/null; then
    sudo dnf install -y python3-gobject gtk4 libadwaita at-spi2-core python3-evdev
elif command -v pacman &>/dev/null; then
    sudo pacman -S --needed python python-gobject gtk4 libadwaita at-spi2-core python-evdev
fi

echo "==> Установка TouchFlow..."
python3 -m pip install --user "\$SRC" 2>/dev/null \\
    || python3 -m pip install --user --break-system-packages "\$SRC"

mkdir -p "\$HOME/.local/share/applications" "\$HOME/.config/systemd/user"
cp "\$SRC/data/com.touchflow.Settings.desktop" "\$HOME/.local/share/applications/"
cp "\$SRC/systemd/touchflow-daemon.service" "\$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now touchflow-daemon.service 2>/dev/null || true
sudo usermod -aG input "\$USER" 2>/dev/null || true

echo ""
echo "✓ TouchFlow установлен!"
echo "  Настройки: touchflow-settings"
echo "  Перелогиньтесь для группы input."
HEADER
chmod +x "$INSTALLER_SH"

echo ""
echo "✓ AppImage:     $OUTPUT"
echo "✓ Portable tar: $TAR_OUT"
echo "✓ Shell installer: $INSTALLER_SH"
echo ""
echo "  chmod +x $OUTPUT && $OUTPUT"
