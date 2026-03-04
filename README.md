# OpenClaw Starter Template for Agencii

Deploy your own private OpenClaw assistant on [Agencii](https://agencii.ai/) in a few clicks.
You can sign in with your regular ChatGPT account using Codex OAuth, so API keys are optional.

**🌐 [Agencii](https://agencii.ai/)** - Cloud platform for deploying and hosting AI agents
**🔗 [GitHub App](https://github.com/apps/agencii)** - Connect your repo for automated deployments

---

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

### 3. Choose your auth path

Recommended path (keyless):

- Use your ChatGPT account with OpenClaw Codex OAuth in Step 6
- No OpenAI API key is required for this path
- OpenClaw Codex auth supports more than Codex-only models (for example `gpt-5.2`)

Optional path (API keys):

- Add provider keys in the Agencii key modal (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- For local development, you can copy `.env.template` to `.env` and set keys there

### 4. Fill the onboarding form

Use the onboarding form in Agencii to set your agent name, description, and instructions.

![Marketplace onboarding form example](https://raw.githubusercontent.com/VRSEN/agency-swarm/main/docs/images/platform/onboarding_form.png)

### 5. Deploy

- Start deployment in Agencii and wait for build completion
- Open deployment shell access for the running sandbox

### 6. Run one-time OpenClaw OAuth bootstrap

Run this in the same deployed sandbox where `main.py` runs:

```bash
openclaw models auth login --provider openai-codex
```

Expected flow (about 1 minute):

1. Command prints an auth URL.
2. Open URL in your local browser and sign in.
3. Paste redirect URL/code back into the shell prompt.
4. OpenClaw writes auth profile files under `/mnt/openclaw/state/...`.

### 7. Verify

After deploy, verify health:

```bash
curl -H "Authorization: Bearer <APP_TOKEN>" https://<your-deployed-domain>/openclaw/health
```

Use the deployment URL shown in Agencii. If your deployment requires auth, use the same `APP_TOKEN` configured for the app.

Expected endpoints include:

- `POST /openclaw/v1/responses`
- `GET /openclaw/health`
- `POST /openclaw/get_response_stream`
- `POST /openclaw/cancel_response_stream`

---

## 🏗️ Project Structure

```text
openclaw-starter-template/
├── main.py                         # FastAPI app entry point
├── agency.py                       # Public agency factory (create_agency)
├── openclaw_template_helpers.py    # Template config + OpenClaw model wiring
├── onboarding_tool.py              # Marketplace onboarding schema/writer
├── onboarding_config.py            # Generated onboarding values
├── .cursor/rules/workflow.mdc      # Cursor workflow guidance
├── Dockerfile                      # Pinned runtime versions
├── requirements.txt                # Python dependencies
└── README.md
```

---

## 🔧 Creating Your OpenClaw Agency

### 🤖 AI-Assisted Setup With Cursor

This template keeps the Cursor workflow files so you can safely customize behavior:

1. Open the repository in Cursor
2. Reference `.cursor/rules/workflow.mdc`
3. Ask Cursor to customize this OpenClaw template (agent name, instructions, tools, UX copy)

### 🛠️ Manual Setup

If you prefer manual setup, update:

- `onboarding_tool.py` (fields shown in marketplace onboarding)
- `openclaw_template_helpers.py` (how onboarding maps to runtime)
- `agency.py` (agency composition)

---

## ⚙️ How This Template Works

- `main.py` starts standard Agency Swarm FastAPI routes via `run_fastapi(...)`
- `attach_openclaw_to_fastapi(...)` mounts OpenClaw proxy routes at `/openclaw/*`
- Agency requests use model id `openclaw:main`
- Proxy forwards to OpenClaw gateway (`127.0.0.1:18789`) with Open Responses compatibility
- OpenClaw state persists under `/mnt/openclaw` in deployed environments

### Runtime defaults

- `OPENCLAW_HOME=/mnt/openclaw`
- `OPENCLAW_STATE_DIR=/mnt/openclaw/state`
- `OPENCLAW_CONFIG_PATH=/mnt/openclaw/openclaw.json`
- `OPENCLAW_LOG_PATH=/mnt/openclaw/logs/openclaw-gateway.log`
- `OPENCLAW_PORT=18789`
- `OPENCLAW_DEFAULT_MODEL=openclaw:main`
- `OPENCLAW_PROVIDER_MODEL=openai/gpt-5-mini` (base fallback in image)

`openclaw:main` is the stable external model id used by Agency Swarm routes.  
This template's onboarding default overrides the provider model to `openai-codex/gpt-5.3-codex` for Codex OAuth flow.

---

## 🧠 Instruction Sources (Important)

Behavior can come from two places:

1. Onboarding instructions (`agent_instructions`)
2. OpenClaw workspace files on persistent storage

Common OpenClaw workspace files:

- `/mnt/openclaw/.openclaw/workspace/AGENTS.md`
- `/mnt/openclaw/.openclaw/workspace/SOUL.md`
- `/mnt/openclaw/.openclaw/workspace/USER.md`
- `/mnt/openclaw/.openclaw/workspace/IDENTITY.md`
- `/mnt/openclaw/.openclaw/workspace/TOOLS.md`
- `/mnt/openclaw/.openclaw/workspace/HEARTBEAT.md`
- `/mnt/openclaw/.openclaw/workspace/MEMORY.md` (optional)

If responses feel off, check both onboarding config and workspace files.

---

## 🚀 Production Deployment With Agencii

### Step 1: Connect repo + auth path

- Use template to create repo
- Connect repo in Agencii
- Use ChatGPT OAuth (recommended) or set provider keys in Agencii key modal

### Step 2: Deploy

- Start deployment from Agencii
- Wait for build completion
- Open your deployed chat UI and run first prompt

### Step 3: Validate

- Verify `/openclaw/health`
- Verify chat streaming in your Agencii UI

---

## 🔨 Development Workflow

### Local development (FastAPI path)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
python main.py
```

Then run:

```bash
curl -H "Authorization: Bearer $APP_TOKEN" http://127.0.0.1:8080/openclaw/health
```

Note: local runtime requires OpenClaw + compatible Node available on your machine (or run via Docker).

### Docker local run (closest to production image)

```bash
docker build -t openclaw-template .
docker run --rm -p 8080:8080 \
  -e APP_TOKEN=local-token \
  -e OPENAI_API_KEY=your_key \
  -v "$PWD/.data:/mnt" \
  openclaw-template
```

---

## 📚 Key Features

- **Deploy in a few clicks** on Agencii with starter template
- **Keyless ChatGPT sign-in** with OpenClaw Codex OAuth
- **OpenClaw + Agency Swarm integration** under one FastAPI app
- **Open Responses compatibility** through `/openclaw/v1/responses`
- **Persistent runtime state** under `/mnt/openclaw`
- **Onboarding-driven customization** without editing core runtime code
- **Pinned runtime versions** in Dockerfile for deterministic builds

---

## 🔐 Security Notes

- This deployment is intended to be a private OpenClaw instance.
- Provider API keys are injected into runtime env so OpenClaw can call provider APIs.
- Do not share one instance across untrusted users.

OpenClaw references:

- [OpenClaw Security Policy](https://github.com/openclaw/openclaw/blob/main/SECURITY.md)
- [OpenClaw Trust Center](https://trust.openclaw.ai)

---

## 📦 Version Pinning And Upgrades

Pinned build args in `Dockerfile`:

- `PYTHON_VERSION=3.13.2`
- `NODE_VERSION=22.14.0`
- `OPENCLAW_VERSION=2026.3.2`

Upgrade policy:

1. Bump versions intentionally (no auto-float)
2. Rebuild image
3. Run local smoke tests + stream checks
4. Promote only after verification

---

## 📖 Learn More

- [Agency Swarm](https://github.com/VRSEN/agency-swarm)
- [OpenClaw Docs](https://docs.openclaw.ai/)
- [Agencii Platform](https://agencii.ai/)

---

## ⚡ Quick Tips

- Start with default onboarding fields; customize only after first successful deploy.
- Keep `openclaw:main` as external model id unless you know downstream impact.
- Put stable persona rules in OpenClaw workspace files (`AGENTS.md`, `SOUL.md`).
- Use Agencii key modal as source of truth for provider credentials.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

### 🌐 Production Route (Recommended)

1. Use this template to create your repository
2. Connect the repository in Agencii
3. Install the [Agencii GitHub App](https://github.com/apps/agencii)
4. Configure keys in Agencii and deploy

### 🛠️ Development Route

1. Run locally with `python main.py`
2. Validate `/openclaw/health` and streaming endpoints
3. Push to your repo and deploy through Agencii

---

## Notes on Agency Swarm dependency

This template currently installs `agency-swarm` from the integration branch:

- `agency-swarm[fastapi] @ git+https://github.com/VRSEN/agency-swarm.git@codex/openclaw-agencii-v1`

Move to an official release tag once OpenClaw integration APIs are published to `main`/PyPI.
