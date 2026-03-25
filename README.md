# OpenClaw Starter Template for Agent Swarm

Deploy your own OpenClaw assistant on [agentswarm.ai](https://agentswarm.ai/) with a guided setup flow.

Use this repository when you want a ready OpenClaw deployment path, not a blank Agency Swarm project.

---

## 🚀 Quick Start

### 1. Use this template

Create your own repository from this template:

- Open [agency-ai-solutions/openclaw-starter-template](https://github.com/agency-ai-solutions/openclaw-starter-template)
- Click **Use this template**
- Create a repository in your own GitHub account/org

### 2. Connect the repository in Agent Swarm

- Sign in to [agentswarm.ai](https://agentswarm.ai/)
- Connect your GitHub account
- Select the repository created from this template

### 3. Add provider secrets

In Agent Swarm, open the swarm deploy form and add only the secrets your deploy actually needs.
Default path:

- Required: `OPENAI_API_KEY`
- Optional: `APP_TOKEN` if you want bearer-token protection on public `/openclaw/*` routes
- Optional: `OPENCLAW_PROVIDER_MODEL` only if you intentionally want a different model or provider
- Optional: `OPENCLAW_GATEWAY_TOKEN` only if you want to override the internal token between Agent Swarm and the local OpenClaw gateway
- Optional: `ANTHROPIC_API_KEY` only if you switch `OPENCLAW_PROVIDER_MODEL` to an Anthropic model
- For local development, copy `.env.template` to `.env`, then fill in only the values you plan to use

### 4. Enable persistent storage

- Turn on **Persistent File Storage** for the swarm before the first deploy
- Set `OPENCLAW_HOME=/app/mnt/openclaw`
- OpenClaw derives its state, config, log, and workspace paths from that root automatically
- This keeps the OpenClaw state alive across rebuilds and redeploys

### 5. Fill the onboarding form

Use the onboarding form in Agent Swarm to define your assistant:

- Name shown in chat
- What it should help with
- Extra instructions you want to add before deploy

Do not put API keys in onboarding fields.

![Marketplace onboarding form example](https://raw.githubusercontent.com/VRSEN/agency-swarm/main/docs/images/platform/onboarding_form.png)

### 6. Deploy

- Start deployment in Agent Swarm and wait for build completion
- The first deploy may take a few extra minutes

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

- [OpenClaw on Agent Swarm](https://github.com/VRSEN/agency-swarm/blob/main/docs/platform/marketplace/openclaw.mdx)

## ⚙️ Advanced Configuration

Only change these if you are intentionally customizing the default setup:

- `OPENCLAW_PROVIDER_MODEL` to switch away from the default `openai/gpt-5.4`
- `APP_TOKEN` to protect FastAPI routes with a bearer token
- `OPENCLAW_GATEWAY_TOKEN` to override the internal token between Agent Swarm and the local OpenClaw gateway
- `ANTHROPIC_API_KEY` or another provider key only if you switch to that provider

## ⚙️ How This Template Works

- `main.py` starts the FastAPI app
- `attach_openclaw_to_fastapi(...)` mounts the OpenClaw proxy at `/openclaw/*`
- `OpenClawAgent` keeps the template code thin and handles the OpenClaw connection behind the scenes
- In deploys, the image uses the pinned OpenClaw runtime directly
- In local non-Docker runs, the template bootstraps the pinned OpenClaw runtime automatically when needed
- OpenClaw runtime uses `OPENCLAW_HOME=/app/mnt/openclaw` in Agent Swarm deploys
- In Agent Swarm's file browser, that same mounted volume appears directly under `/app/mnt/openclaw`

If you want to use OpenClaw inside your own Agency Swarm code, see the [OpenClawAgent framework guide](https://github.com/VRSEN/agency-swarm/blob/main/docs/core-framework/agents/openclaw-agent.mdx).

### What shapes behavior

- The onboarding form sets the assistant name, summary, and extra instructions.
- OpenClaw workspace files under `/app/mnt/openclaw/workspace` (`AGENTS.md`, `SOUL.md`, etc.) are also read by OpenClaw.
- In Agent Swarm's file browser, open `/app/mnt/openclaw/workspace` to edit those files.
- In local Docker runs, mount `.data` to `/app/mnt` so the same files appear on your host under `.data/openclaw/workspace`.
- Both influence behavior, so keep them aligned.

---

## 🧠 Customize Behavior

Default workflow:

- Use onboarding for normal assistant setup
- Use workspace files only when you want persistent OpenClaw behavior
- Use `OPENCLAW_*` environment variables only when you need an explicit override from the pinned template defaults

If responses feel off, check these in order:

1. Onboarding settings from Agent Swarm
2. Workspace files on persistent storage

Advanced internals. Only use these if you want to edit OpenClaw workspace behavior directly:

- File browser path: `/app/mnt/openclaw/workspace/AGENTS.md`
- File browser path: `/app/mnt/openclaw/workspace/SOUL.md`
- File browser path: `/app/mnt/openclaw/workspace/USER.md`
- File browser path: `/app/mnt/openclaw/workspace/MEMORY.md`

## 🔨 Development Workflow

### Local development (FastAPI path)

Use Docker if you want the closest match to production.
Use the FastAPI path below if you want to run everything directly on your machine.
Use Python 3.13 locally to match the production image.
On first startup, the template will download the pinned OpenClaw runtime automatically if it is missing.
Create `.env` from `.env.template` and fill in the values you plan to use.

```bash
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

If your machine blocks the runtime download or you want the closest production match, use the Docker path below instead.

### Docker local run (closest to production image)

First create `.env` from `.env.template` and fill in the provider key your model needs. Then run:

```bash
docker build -t openclaw-template .
docker run --rm -p 8080:8080 \
  --env-file .env \
  -v "$PWD/.data:/app/mnt" \
  openclaw-template
```

That bind mount stores OpenClaw data on your host under `.data/openclaw`.

## 🏗️ Project Structure

```text
openclaw-starter-template/
├── main.py
├── agency.py
├── onboarding_tool.py
├── onboarding_config.py
├── openclaw_template_helpers.py
├── openclaw_runtime_bootstrap.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔐 Security Notes

- This deployment is meant for one team or owner
- Provider API keys are injected into runtime env so OpenClaw can call provider APIs
- Do not share one instance across untrusted users
- If `APP_TOKEN` is unset, the `/openclaw/*` FastAPI routes are not protected
- Set `APP_TOKEN` before deploy if you want bearer-token protection on those routes

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

Pinned runtime versions in this template:

- Python base image: `python:3.13.2-slim`
- Docker Node runtime: `22.22.1`
- OpenClaw runtime: `2026.3.23-2`

The local bootstrap path uses the same pinned OpenClaw runtime from `openclaw_runtime_bootstrap.py`.

Upgrade policy:

1. Bump versions intentionally
2. Rebuild image
3. Run local smoke tests + stream checks
4. Promote only after verification

---

## Notes on Agency Swarm dependency

This template currently installs `agency-swarm` from the OpenClaw worker branch:

- `agency-swarm[fastapi] @ git+https://github.com/VRSEN/agency-swarm.git@codex/openclaw-agent-worker`

Move to an official release tag once OpenClaw integration APIs are published to `main` or PyPI.
