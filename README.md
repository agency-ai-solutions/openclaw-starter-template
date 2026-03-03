# OpenClaw Starter Template for Agencii

This template helps you deploy a private OpenClaw assistant on Agencii in a few clicks.

It keeps Agency Swarm FastAPI endpoints and streaming behavior, while running OpenClaw behind the same app.

## Quick Start

### 1. Use this template

Create your own repo from this template.

### 2. Connect the repo in Agencii

In Agencii, connect your GitHub repo and open the deployment setup.

### 3. Add your model provider keys

Add keys in the Agencii key modal (for example):

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Use whichever providers your OpenClaw model will call.

### 4. Fill the onboarding form

The onboarding form writes `onboarding_config.py` using these fields:

1. `agent_name`
2. `agent_description`
3. `openclaw_model` (default `openclaw:main`)
4. `agent_instructions` (optional)
5. `openclaw_config_overrides_json` (optional)

### 5. Deploy

After deploy, your app exposes:

- `POST /openclaw/v1/responses`
- `GET /openclaw/health`
- Standard Agency Swarm endpoints such as `/{agency}/get_response_stream` and `/{agency}/cancel_response_stream`

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env  # if you have not created .env yet
python main.py
```

Then verify:

```bash
curl -H "Authorization: Bearer $APP_TOKEN" http://127.0.0.1:8080/openclaw/health
```

## How Instructions Work

This is important for behavior tuning.

1. Your onboarding `agent_instructions` are sent on each Open Responses request.
2. OpenClaw merges those instructions into its system prompt.
3. OpenClaw also loads workspace files from disk (persona and operating context).

So if behavior feels different than expected, check both the onboarding text and the OpenClaw workspace files.

### OpenClaw workspace files

With this template defaults, OpenClaw state lives under `/mnt/openclaw`, and workspace bootstrap files are typically under:

- `/mnt/openclaw/.openclaw/workspace/AGENTS.md`
- `/mnt/openclaw/.openclaw/workspace/SOUL.md`
- `/mnt/openclaw/.openclaw/workspace/USER.md`
- `/mnt/openclaw/.openclaw/workspace/IDENTITY.md`
- `/mnt/openclaw/.openclaw/workspace/TOOLS.md`
- `/mnt/openclaw/.openclaw/workspace/HEARTBEAT.md`
- `/mnt/openclaw/.openclaw/workspace/MEMORY.md` (optional)

## Runtime Defaults

- `OPENCLAW_HOME=/mnt/openclaw`
- `OPENCLAW_STATE_DIR=/mnt/openclaw/state`
- `OPENCLAW_CONFIG_PATH=/mnt/openclaw/openclaw.json`
- `OPENCLAW_LOG_PATH=/mnt/openclaw/logs/openclaw-gateway.log`
- `OPENCLAW_PORT=18789`
- `OPENCLAW_DEFAULT_MODEL=openclaw:main`
- `OPENCLAW_PROVIDER_MODEL=openai/gpt-5-mini`

`openclaw:main` is a stable external model id for Agency Swarm routing. The real upstream provider model is controlled by `OPENCLAW_PROVIDER_MODEL`.

## Project Structure

```text
openclaw-starter-template/
├── main.py                         # FastAPI app entry point
├── agency.py                       # Public agency factory (create_agency)
├── openclaw_template_helpers.py    # Template internals and config wiring
├── onboarding_tool.py              # Marketplace onboarding schema/writer
├── onboarding_config.py            # Generated onboarding values
├── Dockerfile                      # Pinned runtime versions
├── requirements.txt                # Python dependencies
└── README.md
```

## Security Notes

- This deployment is intended to be your private OpenClaw instance.
- API keys are injected into the runtime environment so OpenClaw can call provider APIs.
- Do not share one instance across untrusted users.

See OpenClaw security guidance:

- [OpenClaw Security Policy](https://github.com/openclaw/openclaw/blob/main/SECURITY.md)
- [OpenClaw Trust Center](https://trust.openclaw.ai)

## Version Pinning and Upgrades

The Docker image pins runtime versions:

- `PYTHON_VERSION=3.13.2`
- `NODE_VERSION=22.14.0`
- `OPENCLAW_VERSION=2026.3.2`

Upgrade policy:

1. Bump pinned versions intentionally (not automatically).
2. Rebuild the image.
3. Run local smoke tests and stream tests.
4. Promote only after verification.

## Notes on Agency Swarm dependency

The template currently depends on a framework branch that contains OpenClaw integration APIs. Move to an official release tag once those APIs are published in `main`/PyPI.
