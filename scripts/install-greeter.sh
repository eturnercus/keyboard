#!/usr/bin/env bash
# Установка TouchFlow для работы до входа в систему (GDM/LightDM/SDDM)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ $EUID -ne 0 ]]; then
    echo "Запустите с sudo: sudo $0"
    exit 1
fi

echo "==> TouchFlow Greeter Setup"

# Системный пользователь
if ! id touchflow &>/dev/null; then
    useradd -r -s /usr/sbin/nologin -d /var/lib/touchflow touchflow
    mkdir -p /var/lib/touchflow
    chown touchflow:touchflow /var/lib/touchflow
fi

# Установка пакета системно
pip3 install "$ROOT" --break-system-packages 2>/dev/null || pip3 install "$ROOT"

# systemd
cp "$ROOT/systemd/touchflow-greeter.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable touchflow-greeter.service

# Права uinput
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' \
    > /etc/udev/rules.d/99-touchflow-uinput.rules
usermod -aG input touchflow
udevadm control --reload-rules
udevadm trigger

# AT-SPI для greeter
if [[ -d /etc/X11/Xsession.d ]]; then
    cat > /etc/X11/Xsession.d/99touchflow-atspi <<'EOF'
export GTK_MODULES=gail:atk-bridge
export QT_ACCESSIBILITY=1
EOF
fi

echo ""
echo "✓ Greeter service enabled."
echo "  Перезапустите display-manager: sudo systemctl restart gdm|lightdm|sddm"
