#!/bin/bash
# AppImage удаления TouchFlow (Python + C++)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION=$(python3 -c "from touchflow import __version__; print(__version__)")
ARCH=$(uname -m)
case "$ARCH" in
    x86_64|amd64)  APPIMAGE_ARCH="x86_64"; RUNTIME_NAME="runtime-x86_64" ;;
    aarch64|arm64) APPIMAGE_ARCH="aarch64"; RUNTIME_NAME="runtime-aarch64" ;;
    *) echo "Неподдерживаемая архитектура: $ARCH"; exit 1 ;;
esac

APPDIR="$ROOT/build/TouchFlow-Uninstall-${VERSION}-${APPIMAGE_ARCH}.AppDir"
OUTPUT="$ROOT/dist/TouchFlow-Uninstall-${VERSION}-${APPIMAGE_ARCH}.AppImage"
SQUASHFS="$ROOT/build/filesystem-uninstall-${VERSION}.squashfs"
TOOLS="$ROOT/build/tools"
RUNTIME="$TOOLS/${RUNTIME_NAME}"

mkdir -p "$TOOLS" "$ROOT/dist"
rm -rf "$APPDIR" "$SQUASHFS"

install -Dm755 "$ROOT/scripts/uninstall.sh" "$APPDIR/usr/share/touchflow/uninstall.sh"
install -Dm644 "$ROOT/assets/logo.svg" "$APPDIR/touchflow-uninstall.svg"
echo "$VERSION" > "$APPDIR/usr/share/touchflow/VERSION"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
UNINSTALL="${HERE}/usr/share/touchflow/uninstall.sh"

ask() {
  if command -v zenity &>/dev/null; then zenity "$@"; return $?; fi
  if command -v kdialog &>/dev/null; then
    case "$1" in
      --question) kdialog --yesno "${4}" ;;
      --info) kdialog --msgbox "${4}" ;;
    esac
    return $?
  fi
  read -r -p "$4 [y/N] " a
  [[ "${a,,}" == "y" ]]
}

if ask --question --title="TouchFlow Uninstall" --width=480 \
  --text="Удалить TouchFlow (Python и C++)?\n\n• Демоны и systemd\n• Desktop-файлы\n• pip-пакет"; then
  PURGE=""
  if ask --question --title="TouchFlow" --text="Удалить настройки ~/.config/touchflow?"; then
    PURGE="--purge-config"
  fi
  LOG=$(mktemp)
  if bash "$UNINSTALL" -y $PURGE >"$LOG" 2>&1; then
    ask --info --title="TouchFlow" --text="TouchFlow удалён." || cat "$LOG"
  else
    if command -v zenity &>/dev/null; then
      zenity --text-info --title="Ошибка" --filename="$LOG" --width=500 --height=300
    else
      cat "$LOG" >&2
    fi
  fi
  rm -f "$LOG"
fi
APPRUN
chmod +x "$APPDIR/AppRun"

build_with_cat() {
    [[ -f "$RUNTIME" ]] || curl -fsSL -o "$RUNTIME" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/${RUNTIME_NAME}"
    mksquashfs "$APPDIR" "$SQUASHFS" -comp xz -noappend -no-progress
    cat "$RUNTIME" "$SQUASHFS" > "$OUTPUT"
    chmod +x "$OUTPUT"
    rm -f "$SQUASHFS"
}

build_with_cat
file "$OUTPUT" | grep -q "ELF.*executable"
echo "✓ Uninstall AppImage: $OUTPUT"
