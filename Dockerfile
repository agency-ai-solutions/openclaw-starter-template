ARG NODE_VERSION=22.14.0
ARG PYTHON_VERSION=3.13.2
ARG OPENCLAW_VERSION=2026.3.2

FROM node:${NODE_VERSION}-slim AS openclaw-runtime
ARG OPENCLAW_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN update-ca-certificates
RUN git config --global --add url."https://github.com/".insteadOf ssh://git@github.com/ \
    && git config --global --add url."https://github.com/".insteadOf git@github.com:
RUN npm install --global openclaw@${OPENCLAW_VERSION}

FROM python:${PYTHON_VERSION}-slim
ARG OPENCLAW_VERSION

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:${PATH}" \
    OPENCLAW_HOME=/mnt/openclaw \
    OPENCLAW_STATE_DIR=/mnt/openclaw/state \
    OPENCLAW_CONFIG_PATH=/mnt/openclaw/openclaw.json \
    OPENCLAW_LOG_PATH=/mnt/openclaw/logs/openclaw-gateway.log \
    OPENCLAW_PORT=18789 \
    OPENCLAW_DEFAULT_MODEL=openclaw:main

COPY --from=openclaw-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=openclaw-runtime /usr/local/lib/node_modules/openclaw /usr/local/lib/node_modules/openclaw
RUN ln -sf ../lib/node_modules/openclaw/openclaw.mjs /usr/local/bin/openclaw

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
