#!/bin/bash
# Сборка установочного AppImage для TouchFlow C++ (experimental)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CPP="$ROOT/experimental/touchflow-cpp"
VERSION=$(python3 -c "from touchflow import __version__; print(__version__)")
ARCH=$(uname -m)
case "$ARCH" in
    x86_64|amd64)  APPIMAGE_ARCH="x86_64"; RUNTIME_NAME="runtime-x86_64" ;;
    aarch64|arm64) APPIMAGE_ARCH="aarch64"; RUNTIME_NAME="runtime-aarch64" ;;
    *) echo "Неподдерживаемая архитектура: $ARCH (нужен x86_64 или aarch64)"; exit 1 ;;
esac

APPDIR="$ROOT/build/TouchFlow-keyboard-cpp-${VERSION}-${APPIMAGE_ARCH}.AppDir"
OUTPUT="$ROOT/dist/TouchFlow-Keyboard-Cpp-${VERSION}-${APPIMAGE_ARCH}.AppImage"
SQUASHFS="$ROOT/build/filesystem-cpp-${VERSION}.squashfs"
TOOLS="$ROOT/build/tools"
RUNTIME="$TOOLS/${RUNTIME_NAME}"

echo "==> TouchFlow C++ AppImage Builder v${VERSION} (${APPIMAGE_ARCH})"

mkdir -p "$TOOLS" "$ROOT/dist"

echo "==> Building touchflowd-cpp..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq build-essential cmake pkg-config g++ \
        libgtk-4-dev libadwaita-1-dev libevdev-dev libatspi2.0-dev 2>/dev/null || true
fi
CXX=${CXX:-g++} cmake -S "$CPP" -B "$CPP/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$CPP/build" -j"$(nproc)"

rm -rf "$APPDIR" "$SQUASHFS"
mkdir -p "$APPDIR/usr/bin" \
         "$APPDIR/usr/share/touchflow-cpp/data" \
         "$APPDIR/usr/share/icons/hicolor/scalable/apps"

install -m755 "$CPP/build/touchflowd-cpp" "$APPDIR/usr/bin/touchflowd-cpp"
cp "$CPP/data/"*.desktop "$APPDIR/usr/share/touchflow-cpp/data/"
install -m755 "$CPP/bundle-install.sh" "$APPDIR/usr/share/touchflow-cpp/bundle-install.sh"
echo "$VERSION" > "$APPDIR/usr/share/touchflow-cpp/VERSION"
install -Dm644 "$ROOT/assets/logo.svg" "$APPDIR/touchflow-keyboard-cpp.svg"
install -Dm644 "$ROOT/assets/logo.svg" \
    "$APPDIR/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg"

cat > "$APPDIR/touchflow-keyboard-cpp.desktop" <<EOF
[Desktop Entry]
Name=TouchFlow C++ Installer
Comment=Установить TouchFlow C++ (экспериментальная)
Exec=touchflow-cpp-installer
Icon=touchflow-keyboard-cpp
Type=Application
Categories=Utility;System;
Terminal=false
StartupNotify=true
EOF
install -Dm644 "$APPDIR/touchflow-keyboard-cpp.desktop" \
    "$APPDIR/usr/share/applications/touchflow-keyboard-cpp.desktop"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export TOUCHFLOW_CPP_ROOT="${HERE}"
export TOUCHFLOW_CPP_VERSION="$(cat "${HERE}/usr/share/touchflow-cpp/VERSION" 2>/dev/null || echo 1.0.0)"
export APPIMAGE="${APPIMAGE:-${0}}"

show_error() {
    local msg="$1"
    echo "TouchFlow C++ Installer: $msg" >&2
    if command -v zenity &>/dev/null; then
        zenity --error --title="TouchFlow C++" --text="$msg" --width=420 2>/dev/null
    elif command -v kdialog &>/dev/null; then
        kdialog --error "$msg" 2>/dev/null
    fi
}

run_install() {
  export TOUCHFLOW_CPP_ROOT="${HERE}"
  bash "${HERE}/usr/share/touchflow-cpp/bundle-install.sh"
}

if command -v zenity &>/dev/null; then
    if zenity --question --title="TouchFlow C++" --width=480 \
        --text="Установить TouchFlow C++ (экспериментальная)?\n\n• Бинарник touchflowd-cpp\n• KDE виртуальная клавиатура\n• Без Python\n\nПотребуется sudo для зависимостей GTK4."; then
        LOG="$(mktemp)"
        if run_install >"$LOG" 2>&1; then
            zenity --info --title="TouchFlow C++" --width=480 \
                --text="TouchFlow C++ установлен!\n\nЗапуск: touchflowd-cpp\nKDE: Параметры → Виртуальная клавиатура → TouchFlow\n\nПерелогиньтесь для группы input."
        else
            zenity --text-info --title="TouchFlow C++ — ошибка" --width=520 --height=320 \
                --filename="$LOG" 2>/dev/null || cat "$LOG" >&2
        fi
        rm -f "$LOG"
    fi
elif command -v kdialog &>/dev/null; then
    if kdialog --yesno "Установить TouchFlow C++ (экспериментальная)?"; then
        run_install
        kdialog --msgbox "TouchFlow C++ установлен. Запуск: touchflowd-cpp"
    fi
else
    echo "=== TouchFlow C++ Installer ==="
    read -r -p "Установить? [y/N] " ans
    [[ "${ans,,}" == "y" ]] && run_install
fi
APPRUN
chmod +x "$APPDIR/AppRun"

cat > "$APPDIR/usr/bin/touchflow-cpp-installer" <<'WRAPPER'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")/../../.."
export TOUCHFLOW_CPP_ROOT="${HERE}"
exec "${HERE}/AppRun" "$@"
WRAPPER
chmod +x "$APPDIR/usr/bin/touchflow-cpp-installer"

build_with_appimagetool() {
    local tool="$TOOLS/appimagetool-${APPIMAGE_ARCH}.AppImage"
    if [[ ! -f "$tool" ]]; then
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
    mksquashfs "$APPDIR" "$SQUASHFS" -comp xz -noappend -no-progress
    cat "$RUNTIME" "$SQUASHFS" > "$OUTPUT"
    chmod +x "$OUTPUT"
    rm -f "$SQUASHFS"
}

verify_appimage() {
    if ! file "$OUTPUT" | grep -q "ELF.*executable"; then
        echo "ERROR: AppImage не является исполняемым ELF!"
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

cp "$CPP/build/touchflowd-cpp" "$ROOT/dist/touchflowd-cpp-${APPIMAGE_ARCH}"
chmod +x "$ROOT/dist/touchflowd-cpp-${APPIMAGE_ARCH}"

TAR_OUT="$ROOT/dist/TouchFlow-Keyboard-Cpp-${VERSION}-${APPIMAGE_ARCH}.tar.gz"
tar -czf "$TAR_OUT" -C "$ROOT/build" "$(basename "$APPDIR")"

INSTALLER_SH="$ROOT/dist/touchflow-install-cpp-${VERSION}.sh"
cat > "$INSTALLER_SH" <<HEADER
#!/bin/bash
# TouchFlow C++ — универсальный shell-установщик
set -euo pipefail
REPO="https://github.com/eturnercus/keyboard"
TMP=\$(mktemp -d)
trap 'rm -rf "\$TMP"' EXIT

echo "==> TouchFlow C++ Installer v${VERSION}"
echo "    Архитектура: \$(uname -m)"

echo "==> Скачивание..."
curl -fsSL "\${REPO}/archive/refs/heads/main.tar.gz" -o "\$TMP/src.tar.gz"
tar -xzf "\$TMP/src.tar.gz" -C "\$TMP"
SRC="\$TMP/keyboard-main"

echo "==> Установка..."
bash "\$SRC/scripts/install-cpp.sh"
HEADER
chmod +x "$INSTALLER_SH"

echo ""
echo "✓ AppImage:        $OUTPUT"
echo "✓ Portable tar:    $TAR_OUT"
echo "✓ Shell installer: $INSTALLER_SH"
echo ""
echo "  chmod +x $OUTPUT && $OUTPUT"
