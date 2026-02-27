ARG NODE_VERSION=22.14.0
ARG PYTHON_VERSION=3.13.2
ARG OPENCLAW_VERSION=2026.2.26

FROM node:${NODE_VERSION}-slim AS openclaw-runtime
ARG OPENCLAW_VERSION
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
    OPENCLAW_DEFAULT_MODEL=openclaw:main \
    OPENCLAW_PROVIDER_MODEL=openai/gpt-4o-mini

COPY --from=openclaw-runtime /usr/local/ /usr/local/

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
