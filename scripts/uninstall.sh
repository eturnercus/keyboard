#!/usr/bin/env bash
# TouchFlow — универсальное удаление Python и C++ версий
set -euo pipefail

PURGE_CONFIG=false
YES=false

usage() {
    echo "Использование: $0 [--purge-config] [-y]"
    echo "  --purge-config  Удалить ~/.config/touchflow"
    echo "  -y              Без подтверждения"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --purge-config) PURGE_CONFIG=true; shift ;;
        -y|--yes) YES=true; shift ;;
        -h|--help) usage ;;
        *) echo "Неизвестный аргумент: $1"; usage ;;
    esac
done

if [[ "$YES" != true ]]; then
    echo "Будут удалены TouchFlow Python и C++ (демоны, desktop, systemd, pip)."
    [[ "$PURGE_CONFIG" == true ]] && echo "Также: ~/.config/touchflow"
    read -r -p "Продолжить? [y/N] " ans
    [[ "${ans,,}" == "y" ]] || exit 0
fi

echo "==> Остановка служб..."
systemctl --user disable --now touchflow-daemon.service 2>/dev/null || true
systemctl --user disable --now touchflow-daemon-cpp.service 2>/dev/null || true

echo "==> Удаление systemd units..."
rm -f "${HOME}/.config/systemd/user/touchflow-daemon.service"
rm -f "${HOME}/.config/systemd/user/touchflow-daemon-cpp.service"
systemctl --user daemon-reload 2>/dev/null || true

echo "==> Удаление бинарников..."
for bin in touchflowd touchflowd-cpp touchflow-settings touchflow-settings-cpp \
           touchflow-cli touchflow-installer touchflowd-wrapper touchflow-doctor; do
    rm -f "${HOME}/.local/bin/${bin}"
done

echo "==> Удаление desktop-файлов..."
rm -f "${HOME}/.local/share/applications/com.touchflow."*.desktop

echo "==> Удаление D-Bus activation..."
rm -f "${HOME}/.local/share/dbus-1/services/com.touchflow.Keyboard.service"

echo "==> Удаление Python-пакета..."
python3 -m pip uninstall -y touchflow-keyboard 2>/dev/null \
    || python3 -m pip uninstall -y touchflow-keyboard --break-system-packages 2>/dev/null \
    || true

if [[ "$PURGE_CONFIG" == true ]]; then
    echo "==> Удаление конфигурации..."
    rm -rf "${HOME}/.config/touchflow"
    rm -rf "${HOME}/.local/share/touchflow"
fi

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
fi
for cmd in kbuildsycoca6 kbuildsycoca5; do
    command -v "$cmd" &>/dev/null && "$cmd" --noincremental 2>/dev/null && break
done

echo ""
echo "✓ TouchFlow (Python и C++) удалён."
echo "  Перезапустите сессию или KWin, если виртуальная клавиатура осталась в списке KDE."
