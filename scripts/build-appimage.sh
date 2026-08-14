#!/bin/bash
# Сборка установочного AppImage для TouchFlow Keyboard
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(python3 -c "from touchflow import __version__; print(__version__)")
APPDIR="$ROOT/build/TouchFlow-keyboard-${VERSION}-x86_64.AppDir"
OUTPUT="$ROOT/dist/TouchFlow-Keyboard-${VERSION}-x86_64.AppImage"
TOOLS="$ROOT/build/tools"

echo "==> TouchFlow AppImage Builder v${VERSION}"

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/share/touchflow" "$APPDIR/usr/bin" "$TOOLS" "$ROOT/dist"

# Копируем проект
mkdir -p "$APPDIR/usr/share/touchflow"
tar -C "$ROOT" --exclude='./build' --exclude='./dist' --exclude='./.git' -cf - . \
    | tar -C "$APPDIR/usr/share/touchflow" -xf -

# Иконка
install -Dm644 "$ROOT/assets/logo.svg" "$APPDIR/touchflow-keyboard.svg"
install -Dm644 "$ROOT/assets/logo.svg" \
    "$APPDIR/usr/share/icons/hicolor/scalable/apps/com.touchflow.Keyboard.svg"

# Desktop entry
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

# AppRun — запускает графический установщик
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
    local tool="$TOOLS/appimagetool-x86_64.AppImage"
    if [[ ! -f "$tool" ]]; then
        echo "==> Downloading appimagetool..."
        curl -fsSL -o "$tool" \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        chmod +x "$tool"
    fi
    ARCH=x86_64 "$tool" --appimage-extract-and-run "$APPDIR" "$OUTPUT" 2>/dev/null \
        || ARCH=x86_64 "$tool" "$APPDIR" "$OUTPUT"
}

build_with_mksquashfs() {
    local runtime="$TOOLS/runtime-x86_64"
    if [[ ! -f "$runtime" ]]; then
        echo "==> Downloading AppImage runtime..."
        curl -fsSL -o "$runtime" \
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/runtime-x86_64"
    fi
    cp "$runtime" "$OUTPUT"
    chmod +x "$OUTPUT"
    local offset
    offset=$(stat -c%s "$OUTPUT")
    mksquashfs "$APPDIR" "$OUTPUT" -offset "$offset" -comp xz -noappend -no-progress
}

echo "==> Building AppImage..."
if command -v mksquashfs &>/dev/null; then
    build_with_mksquashfs
elif command -v fuse &>/dev/null || [[ -e /dev/fuse ]]; then
    build_with_appimagetool
else
    # Попытка через mksquashfs после установки
    sudo apt-get install -y squashfs-tools 2>/dev/null || true
    if command -v mksquashfs &>/dev/null; then
        build_with_mksquashfs
    else
        build_with_appimagetool
    fi
fi

# Также создаём portable tar для систем без FUSE
TAR_OUT="$ROOT/dist/TouchFlow-Keyboard-${VERSION}-x86_64.tar.gz"
tar -czf "$TAR_OUT" -C "$ROOT/build" "$(basename "$APPDIR")"

echo ""
echo "✓ AppImage: $OUTPUT"
echo "✓ Portable: $TAR_OUT"
echo ""
echo "  chmod +x $OUTPUT"
echo "  ./dist/TouchFlow-Keyboard-${VERSION}-x86_64.AppImage"
