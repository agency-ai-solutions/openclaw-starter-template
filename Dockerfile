FROM ubuntu:22.04
ARG NODE_VERSION=22.22.1
ARG OPENCLAW_VERSION=2026.3.23-2
ARG PYTHON_VERSION=3.13

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:${PATH}" \
    NODE_OPTIONS=--max-old-space-size=768 \
    CHROME_BIN=/usr/local/bin/openclaw-browser \
    OPENCLAW_HOME=/app/mnt/openclaw \
    OPENCLAW_PORT=18789 \
    OPENCLAW_STARTUP_TIMEOUT_SECONDS=180 \
    OPENCLAW_DEFAULT_MODEL=openclaw:main \
    OPENCLAW_PROVIDER_MODEL=openai/gpt-5.4 \
    DISPLAY=:1 \
    XVFB_WHD=1920x1080x24 \
    VNC_PORT=5900 \
    NOVNC_PORT=6080 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    MESA_LOADER_DRIVER_OVERRIDE=llvmpipe

WORKDIR /app

RUN apt-get update && \
    if command -v unminimize >/dev/null 2>&1; then yes | unminimize; fi && \
    apt-get install --yes --no-install-recommends \
      ca-certificates \
      curl \
      dbus-x11 \
      ffmpeg \
      fonts-dejavu-core \
      fonts-liberation \
      fonts-noto \
      fonts-noto-color-emoji \
      fonts-ubuntu \
      galculator \
      gedit \
      git \
      gnupg \
      libasound2 \
      libatk-bridge2.0-0 \
      libgbm1 \
      libgtk-3-0 \
      libnspr4 \
      libnss3 \
      libu2f-udev \
      libvulkan1 \
      libreoffice \
      mesa-utils \
      mesa-vulkan-drivers \
      net-tools \
      netcat-openbsd \
      pcmanfm \
      python3-launchpadlib \
      scrot \
      software-properties-common \
      sudo \
      tint2 \
      util-linux \
      wget \
      x11-apps \
      x11-utils \
      x11-xserver-utils \
      x11vnc \
      xauth \
      xdotool \
      xorg \
      xpaint \
      xpdf \
      xserver-xorg \
      xfce4 \
      xfce4-goodies \
      xfce4-terminal \
      xvfb \
      xz-utils && \
    update-ca-certificates && \
    add-apt-repository --yes ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install --yes --no-install-recommends \
      "python${PYTHON_VERSION}" \
      "python${PYTHON_VERSION}-venv" && \
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && \
    "python${PYTHON_VERSION}" /tmp/get-pip.py && \
    ln -sf "/usr/bin/python${PYTHON_VERSION}" /usr/local/bin/python3 && \
    ln -sf "/usr/bin/python${PYTHON_VERSION}" /usr/local/bin/python && \
    ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip3 && \
    ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip && \
    rm -f /tmp/get-pip.py && \
    update-ca-certificates && \
    arch="$(dpkg --print-architecture)" && \
    case "$arch" in \
      amd64) node_arch="x64" ;; \
      arm64) node_arch="arm64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac && \
    case "$arch" in \
      amd64) \
        curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
        apt-get update && \
        apt-get install --yes --no-install-recommends google-chrome-stable \
      ;; \
      arm64) \
        apt-get install --yes --no-install-recommends epiphany-browser \
      ;; \
    esac && \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" -o /tmp/node.tar.xz && \
    tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 --no-same-owner && \
    rm /tmp/node.tar.xz && \
    git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/ && \
    git config --global --add url."https://github.com/".insteadOf git@github.com: && \
    git clone --branch e2b-desktop https://github.com/e2b-dev/noVNC.git /opt/noVNC && \
    ln -sf /opt/noVNC/vnc.html /opt/noVNC/index.html && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -sf /usr/bin/xfce4-terminal.wrapper /etc/alternatives/x-terminal-emulator && \
    npm install --global "openclaw@${OPENCLAW_VERSION}" && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
COPY browser_launcher.sh /usr/local/bin/openclaw-browser
COPY start_command.sh /start_command.sh
RUN chmod +x /start_command.sh /usr/local/bin/openclaw-browser && \
    if [ -f /usr/share/applications/google-chrome.desktop ]; then \
      sed -i 's#^Exec=.*#Exec=/usr/local/bin/openclaw-browser %U#' /usr/share/applications/google-chrome.desktop; \
    fi && \
    if [ -f /usr/share/applications/org.gnome.Epiphany.desktop ]; then \
      sed -i 's#^Exec=.*#Exec=/usr/local/bin/openclaw-browser %U#' /usr/share/applications/org.gnome.Epiphany.desktop; \
    fi && \
    update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/local/bin/openclaw-browser 200 && \
    update-alternatives --install /usr/bin/gnome-www-browser gnome-www-browser /usr/local/bin/openclaw-browser 200

# update as necessary in accordance with the security policy
USER root

EXPOSE 5900 6080 8080

CMD ["/start_command.sh"]
