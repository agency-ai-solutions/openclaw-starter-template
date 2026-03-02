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
2. Set provider keys in the Agencii key modal (BYOK), for example:
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

## Runtime defaults (`/mnt` persistence)

`openclaw:main` stays as the external model id, while `OPENCLAW_PROVIDER_MODEL` controls which provider model runs upstream.

- `OPENCLAW_HOME=/mnt/openclaw`
- `OPENCLAW_STATE_DIR=/mnt/openclaw/state`
- `OPENCLAW_CONFIG_PATH=/mnt/openclaw/openclaw.json`
- `OPENCLAW_LOG_PATH=/mnt/openclaw/logs/openclaw-gateway.log`
- `OPENCLAW_PORT=18789`
- `OPENCLAW_PROVIDER_MODEL=openai/gpt-5-mini`

## Shared instructions behavior

- `shared_instructions.md` is loaded and prepended to the agent instructions at runtime.
- This applies to the OpenClaw-backed agent too.
- If the file is missing, the template now falls back to no shared instructions (instead of passing a filename literal as instruction text).

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

`requirements.txt` is pinned to an Agency Swarm commit that includes OpenClaw integration APIs used by this template.

Upgrade rule:

1. Move to an official Agency Swarm release once it includes `agency_swarm.integrations.openclaw`.
2. Re-run template deploy smoke tests before publishing changes.

## Local run

```bash
pip install -r requirements.txt
python main.py
```

Local note: if your machine does not provide writable `/mnt`, set `OPENCLAW_HOME`, `OPENCLAW_STATE_DIR`, `OPENCLAW_CONFIG_PATH`, and `OPENCLAW_LOG_PATH` to a writable local path.

Then call:

- `http://localhost:8080/openclaw/health`
- `http://localhost:8080/openclaw/v1/responses`

## Files to customize

- `agency.py` - agent definition and model wiring
- `onboarding_tool.py` - marketplace onboarding schema
- `onboarding_config.py` - default committed onboarding config
- `main.py` - FastAPI app + OpenClaw mount
