FROM python:3.13.2-slim
ARG NODE_VERSION=22.14.0
ARG OPENCLAW_VERSION=2026.3.23-2

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:${PATH}" \
    OPENCLAW_HOME=/mnt/openclaw \
    OPENCLAW_STATE_DIR=/mnt/openclaw/state \
    OPENCLAW_CONFIG_PATH=/mnt/openclaw/openclaw.json \
    OPENCLAW_LOG_PATH=/mnt/openclaw/logs/openclaw-gateway.log \
    OPENCLAW_PORT=18789 \
    OPENCLAW_DEFAULT_MODEL=openclaw:main

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes --no-install-recommends ca-certificates curl git xz-utils && \
    rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates && \
    arch="$(dpkg --print-architecture)" && \
    case "$arch" in \
      amd64) node_arch="x64" ;; \
      arm64) node_arch="arm64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac && \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" -o /tmp/node.tar.xz && \
    tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 --no-same-owner && \
    rm /tmp/node.tar.xz && \
    git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/ && \
    git config --global --add url."https://github.com/".insteadOf git@github.com: && \
    npm install --global "openclaw@${OPENCLAW_VERSION}" && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
