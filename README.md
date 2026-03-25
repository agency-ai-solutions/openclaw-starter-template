# OpenClaw Starter Template for Agencii

Deploy OpenClaw on Agencii in one click with Agency Swarm FastAPI endpoints unchanged.

## What this template does

- Runs a standard Agency Swarm FastAPI app.
- Mounts OpenClaw proxy endpoints:
  - `POST /openclaw/v1/responses`
  - `GET /openclaw/health`
- Uses one default agent backed by OpenClaw via `openclaw:main`.
- Keeps stream + cancel on normal Agency Swarm routes:
  - `/{agency}/get_response_stream`
  - `/{agency}/cancel_response_stream`

## One-click deploy flow (Agencii)

1. Connect this repo in Agencii.
2. Set provider keys in the Agencii key modal, for example:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
3. Fill onboarding form fields.
4. Deploy.

## Onboarding form fields

Defined in `onboarding_tool.py`:

1. `agent_name`
2. `agent_description`
3. `openclaw_model` (default `openclaw:main`)
4. `agent_instructions` (optional)
5. `openclaw_config_overrides_json` (optional)

Running `python onboarding_tool.py` writes `onboarding_config.py`.

## Runtime defaults (Agent Swarm persistent storage)

`openclaw:main` stays as the external model id, while `OPENCLAW_PROVIDER_MODEL` controls which provider model runs upstream.

- `OPENCLAW_HOME=/app/mnt/openclaw`
- `OPENCLAW_PORT=18789`
- `OPENCLAW_PROVIDER_MODEL=openai/gpt-5.4`

From `OPENCLAW_HOME`, the framework derives:

- `OPENCLAW_STATE_DIR=<OPENCLAW_HOME>/state`
- `OPENCLAW_CONFIG_PATH=<OPENCLAW_HOME>/openclaw.json`
- `OPENCLAW_LOG_PATH=<OPENCLAW_HOME>/logs/openclaw-gateway.log`

## Instructions behavior

- The OpenClaw agent instructions come from the onboarding field `agent_instructions`.
- This template does not apply agency-level shared instructions by default.
- Proxy authentication uses `APP_TOKEN` by default; `OPENCLAW_GATEWAY_TOKEN` is a fallback when `APP_TOKEN` is unset.
- To change behavior, update `agent_instructions` in onboarding or edit `agency.py`.

## Deterministic build policy

Pinned in `Dockerfile`:

- `PYTHON_VERSION=3.13.2`
- `NODE_VERSION=22.14.0`
- `OPENCLAW_VERSION=2026.2.26`

Upgrade rule:

1. Bump pinned versions.
2. Rebuild image.
3. Re-run integration/E2E checks.
4. Deploy only after validation.

## Agency Swarm dependency pin

`requirements.txt` is pinned to an immutable Agency Swarm commit that includes OpenClaw integration APIs used by this template.

Upgrade rule:

1. Move to an official Agency Swarm release (or merged `main` SHA) once it includes `agency_swarm.integrations.openclaw`.
2. Re-run template deploy smoke tests before publishing changes.

## Local run

```bash
pip install -r requirements.txt
python main.py
```

Local Node requirement:

- OpenClaw requires Node `>=22.12.0`.
- If you have multiple Node installs, set `OPENCLAW_NODE_BIN` to the compatible binary path (for example `/opt/homebrew/bin/node` on macOS).

Local note: if your machine does not provide writable `/app/mnt`, set `OPENCLAW_HOME` to a writable local path and let the derived paths follow it.

Then call:

- `http://localhost:8080/openclaw/health`
- `http://localhost:8080/openclaw/v1/responses`

## Files to customize

- `agency.py` - agent definition and model wiring
- `onboarding_tool.py` - marketplace onboarding schema
- `onboarding_config.py` - default committed onboarding config
- `main.py` - FastAPI app + OpenClaw mount
