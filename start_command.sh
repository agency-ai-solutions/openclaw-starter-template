#!/usr/bin/env bash
set -euo pipefail

trim_value() {
    printf '%s' "$1" | awk '{$1=$1; print}'
}

normalize_port() {
    local raw_value normalized_value default_value
    raw_value="${1:-}"
    default_value="$2"
    normalized_value="$(trim_value "${raw_value:-$default_value}")"

    case "${normalized_value}" in
        ''|*[!0-9]*)
            printf '%s' "${default_value}"
            ;;
        *)
            printf '%s' "${normalized_value}"
            ;;
    esac
}

export DISPLAY="$(trim_value "${DISPLAY:-:1}")"
export XVFB_WHD="$(trim_value "${XVFB_WHD:-1920x1080x24}")"
export VNC_PORT="$(normalize_port "${VNC_PORT:-5900}" "5900")"
export NOVNC_PORT="$(normalize_port "${NOVNC_PORT:-6080}" "6080")"
export XDG_RUNTIME_DIR="$(trim_value "${XDG_RUNTIME_DIR:-/tmp/runtime-root}")"

mkdir -p "${XDG_RUNTIME_DIR}" /tmp/.X11-unix /var/run/dbus
chmod 700 "${XDG_RUNTIME_DIR}"

Xvfb "${DISPLAY}" -screen 0 "${XVFB_WHD}" -ac +extension RANDR +extension RENDER >/tmp/xvfb.log 2>&1 &

for _ in $(seq 1 30); do
    if xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if command -v dbus-launch >/dev/null 2>&1; then
    dbus-launch --exit-with-session xfce4-session >/tmp/xfce4.log 2>&1 &
else
    xfce4-session >/tmp/xfce4.log 2>&1 &
fi

x11vnc \
    -display "${DISPLAY}" \
    -forever \
    -shared \
    -nopw \
    -rfbport "${VNC_PORT}" \
    -bg \
    -o /tmp/x11vnc.log

/opt/noVNC/utils/novnc_proxy \
    --vnc "localhost:${VNC_PORT}" \
    --listen "${NOVNC_PORT}" \
    >/tmp/novnc.log 2>&1 &

exec python -u main.py
