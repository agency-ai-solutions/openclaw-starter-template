#!/usr/bin/env bash
set -euo pipefail

log_file=/tmp/browser-launcher.log

if command -v google-chrome-stable >/dev/null 2>&1; then
    mkdir -p /tmp/google-chrome-profile
    exec google-chrome-stable \
        --no-sandbox \
        --disable-dev-shm-usage \
        --disable-gpu \
        --ozone-platform=x11 \
        --password-store=basic \
        --user-data-dir=/tmp/google-chrome-profile \
        "$@" >>"${log_file}" 2>&1
fi

if command -v epiphany-browser >/dev/null 2>&1; then
    exec epiphany-browser "$@" >>"${log_file}" 2>&1
fi

echo "No supported graphical browser is installed." | tee -a "${log_file}" >&2
exit 1
