FROM ubuntu:22.04
ARG NODE_VERSION=22.22.1
ARG OPENCLAW_VERSION=2026.3.23-2
ARG PYTHON_VERSION=3.13

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:${PATH}" \
    NODE_OPTIONS=--max-old-space-size=768 \
    OPENCLAW_HOME=/app/mnt/openclaw \
    OPENCLAW_PORT=18789 \
    OPENCLAW_STARTUP_TIMEOUT_SECONDS=180 \
    OPENCLAW_DEFAULT_MODEL=openclaw:main \
    OPENCLAW_PROVIDER_MODEL=openai/gpt-5.4

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
      ca-certificates \
      curl \
      git \
      gnupg \
      software-properties-common \
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

# update as necessary in accordance with the security policy
USER root

CMD ["python", "-u", "main.py"]
