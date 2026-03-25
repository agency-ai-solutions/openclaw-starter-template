# OpenClaw Starter Template for Agencii

Deploy your own private OpenClaw assistant on [Agencii](https://agencii.ai/) in a few clicks.

Use this repository when you want a ready OpenClaw deployment path, not a blank Agency Swarm project.

## 🚀 Quick Start

### 1. Use this template

Create your own repository from this template:

- Open [agency-ai-solutions/openclaw-starter-template](https://github.com/agency-ai-solutions/openclaw-starter-template)
- Click **Use this template**
- Create a repository in your own GitHub account/org

### 2. Connect the repository in Agencii

- Sign in to [agencii.ai](https://agencii.ai/)
- Connect your GitHub account
- Select the repository created from this template

### 3. Add provider secrets

- Default deploy: add `OPENAI_API_KEY`
- Optional: set `APP_TOKEN` if you want protected FastAPI routes
- Advanced: only set `OPENCLAW_PROVIDER_MODEL`, `OPENCLAW_GATEWAY_TOKEN`, or another provider key if you are intentionally changing the default setup
- For local development, copy `.env.template` to `.env`, then fill in the values you actually plan to use

### 4. Enable persistent storage

- Turn on **Persistent File Storage** for the swarm before the first deploy
- Set `OPENCLAW_HOME=/app/mnt/openclaw`
- OpenClaw derives its state, config, and log paths from that root automatically
### 5. Fill the onboarding form

Use the onboarding form in Agencii to define your assistant:

- Name shown in chat
- What it should help with
- Extra instructions you want to add before deploy

Do not put API keys in onboarding fields.

![Marketplace onboarding form example](https://raw.githubusercontent.com/VRSEN/agency-swarm/main/docs/images/platform/onboarding_form.png)

### 6. Deploy

- Start deployment in Agencii and wait for build completion

### 7. Verify

After deploy, open the chat and send your first message.
If you want a quick health check too, call:

```bash
curl https://<your-deployed-domain>/openclaw/health
```

If your deployment uses `APP_TOKEN`, add the same bearer token to the request.

```bash
curl -H "Authorization: Bearer <APP_TOKEN>" https://<your-deployed-domain>/openclaw/health
```

For the full platform walkthrough, see:

- [OpenClaw on Agencii](https://github.com/VRSEN/agency-swarm/blob/main/docs/platform/marketplace/openclaw.mdx)

## ⚙️ How This Template Works

- `main.py` starts the FastAPI app
- `attach_openclaw_to_fastapi(...)` mounts the OpenClaw proxy at `/openclaw/*`
- `OpenClawAgent` keeps the template code thin and handles the OpenClaw connection behind the scenes
- OpenClaw runtime uses `OPENCLAW_HOME=/app/mnt/openclaw` in Agent Swarm deploys
- In Agent Swarm's file browser, that same mounted volume appears directly under `/app/mnt/openclaw`

If you want to use OpenClaw inside your own Agency Swarm code, see the [OpenClawAgent framework guide](https://github.com/VRSEN/agency-swarm/blob/main/docs/core-framework/agents/openclaw-agent.mdx).

### What shapes behavior

- The onboarding form sets the assistant name, summary, and extra instructions.
- OpenClaw workspace files under `/app/mnt/openclaw/.openclaw/workspace` (`AGENTS.md`, `SOUL.md`, etc.) are also read by OpenClaw.
- In Agent Swarm's file browser, open `/app/mnt/openclaw/.openclaw/workspace` to edit those files.
- In local Docker runs, the same files appear on your host under `.data/openclaw/.openclaw/workspace` because `.data` is mounted to `/mnt`.
- Both influence behavior, so keep them aligned.

---

## 🧠 Customize Behavior

If responses feel off, check both places that shape behavior:

1. onboarding settings from Agencii
2. OpenClaw workspace files on persistent storage

Common workspace files:

- File browser path: `/app/mnt/openclaw/.openclaw/workspace/AGENTS.md`
- File browser path: `/app/mnt/openclaw/.openclaw/workspace/SOUL.md`
- File browser path: `/app/mnt/openclaw/.openclaw/workspace/USER.md`
- File browser path: `/app/mnt/openclaw/.openclaw/workspace/MEMORY.md`

---

## 🔨 Development Workflow

### Local development (FastAPI path)

Use Docker if you want the closest match to production.
Use the FastAPI path below if you want to run everything directly on your machine.
Python 3.13 is the safest local choice for this template.
This path assumes `nvm` and Python 3.13 are already installed locally.

```bash
nvm install 22.14.0
nvm use 22.14.0
npm install -g openclaw@2026.3.23-2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env now. The default model uses OPENAI_API_KEY with OpenAI GPT-5.4.
set -a; source .env; set +a
python main.py
```

Then run one of these:

```bash
curl http://127.0.0.1:8080/openclaw/health
```

If you set `APP_TOKEN`, use:

```bash
curl -H "Authorization: Bearer $APP_TOKEN" http://127.0.0.1:8080/openclaw/health
```

Local runtime needs OpenClaw plus Node `>=22.12.0`.
If you do not have that on your machine, use the Docker path below instead.

### Docker local run (closest to production image)

First create `.env` from `.env.template` and fill in the provider key your model needs. Then run:
This path assumes Docker is already installed and running.

```bash
docker build -t openclaw-template .
docker run --rm -p 8080:8080 \
  --env-file .env \
  -v "$PWD/.data:/mnt" \
  openclaw-template
```

## 🔐 Security Notes

- This deployment is intended to be a private OpenClaw instance.
- Provider API keys are injected into runtime env so OpenClaw can call provider APIs.
- Do not share one instance across untrusted users.

OpenClaw references:

- [OpenClaw Security Policy](https://github.com/openclaw/openclaw/blob/main/SECURITY.md)
- [OpenClaw Trust Center](https://trust.openclaw.ai)

## Advanced Model Changes

The default setup uses:

- `OPENAI_API_KEY`
- `OPENCLAW_PROVIDER_MODEL=openai/gpt-5.4`

Only change `OPENCLAW_PROVIDER_MODEL` if you intentionally want a different provider or model.
If you do that, add the matching provider secret too.

`OPENCLAW_GATEWAY_TOKEN` is optional.
Leave it unset unless you need to override the internal token used between Agency Swarm and the local OpenClaw gateway.

---

## 📦 Version Pinning And Upgrades

Pinned runtime versions in `Dockerfile`:

- Python base image: `python:3.13.2-slim`
- `NODE_VERSION=22.14.0`
- `OPENCLAW_VERSION=2026.3.23-2`

Upgrade policy:

1. Bump versions intentionally (no auto-float)
2. Rebuild image
3. Run local smoke tests + stream checks
4. Promote only after verification

---

## Notes on Agency Swarm dependency

This template currently installs `agency-swarm` from the OpenClaw worker branch:

- `agency-swarm[fastapi] @ git+https://github.com/VRSEN/agency-swarm.git@codex/openclaw-agent-worker`

Move to an official release tag once OpenClaw integration APIs are published to `main`/PyPI.
