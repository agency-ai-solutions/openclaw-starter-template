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
    OPENCLAW_HOME=/app/mnt/openclaw \
    OPENCLAW_PORT=18789 \
    OPENCLAW_DEFAULT_MODEL=openclaw:main \
    OPENCLAW_PROVIDER_MODEL=openai/gpt-5.4

COPY --from=openclaw-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=openclaw-runtime /usr/local/bin/openclaw /usr/local/bin/openclaw
COPY --from=openclaw-runtime /usr/local/lib/node_modules/openclaw /usr/local/lib/node_modules/openclaw

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
