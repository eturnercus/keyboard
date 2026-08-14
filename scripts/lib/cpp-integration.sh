#!/usr/bin/env bash
# Общая системная интеграция TouchFlow C++
set -euo pipefail

register_kde_cpp() {
    local desktop_id="com.touchflow.Keyboard.Virtual.desktop"
    for writer in kwriteconfig6 kwriteconfig5; do
        if command -v "$writer" &>/dev/null; then
            "$writer" --file kwinrc --group Wayland --key InputMethod "$desktop_id" 2>/dev/null || true
            "$writer" --file kwinrc --group Wayland --key VirtualKeyboardEnabled true 2>/dev/null || true
            break
        fi
    done
}

ensure_local_bin_path() {
    local bin_dir="${HOME}/.local/bin"
    mkdir -p "$bin_dir"
    for f in "${HOME}/.profile" "${HOME}/.bashrc"; do
        [[ -f "$f" ]] || continue
        grep -q "$bin_dir" "$f" 2>/dev/null && continue
        echo "export PATH=\"${bin_dir}:\$PATH\"  # TouchFlow" >> "$f"
    done
}

install_cpp_systemd() {
    local bin="${HOME}/.local/bin/touchflowd-cpp"
    local svc_dir="${HOME}/.config/systemd/user"
    mkdir -p "$svc_dir"
    cat > "${svc_dir}/touchflow-daemon-cpp.service" <<EOF
[Unit]
Description=TouchFlow C++ On-Screen Keyboard
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=${bin}
Restart=on-failure
RestartSec=3
Environment=GTK_USE_PORTAL=0
Environment=AT_SPI_BUS_ADDRESS=unix:path=/run/user/%U/at-spi/bus

[Install]
WantedBy=graphical-session.target
EOF
    systemctl --user daemon-reload 2>/dev/null || true
    systemctl --user enable --now touchflow-daemon-cpp.service 2>/dev/null || true
}
