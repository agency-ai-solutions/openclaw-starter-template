#!/usr/bin/env bash
set -euo pipefail

if command -v google-chrome-stable >/dev/null 2>&1; then
    exec google-chrome-stable \
        --no-sandbox \
        --disable-dev-shm-usage \
        --disable-gpu \
        --password-store=basic \
        --user-data-dir=/tmp/google-chrome-profile \
        "$@"
fi

if command -v epiphany-browser >/dev/null 2>&1; then
    exec epiphany-browser "$@"
fi

echo "No supported graphical browser is installed." >&2
exit 1
