from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from agency_swarm import Agency, Agent
from agency_swarm.integrations.openclaw import build_openclaw_responses_model

load_dotenv()

_DEFAULT_ONBOARDING_CONFIG: dict[str, str] = {
    "agent_name": "OpenClaw Agent",
    "agent_description": "Agent powered by an OpenClaw Responses backend.",
    "openclaw_model": "openclaw:main",
    "agent_instructions": "Handle user tasks and call tools when needed.",
    "openclaw_config_overrides_json": "",
}

try:
    from onboarding_config import config as onboarding_config
except ImportError:
    onboarding_config = _DEFAULT_ONBOARDING_CONFIG


def _get_config_value(key: str) -> str:
    value = onboarding_config.get(key, _DEFAULT_ONBOARDING_CONFIG.get(key, ""))
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def _apply_openclaw_config_overrides() -> None:
    raw_overrides = _get_config_value("openclaw_config_overrides_json")
    if not raw_overrides:
        os.environ.setdefault("OPENCLAW_PROXY_API_KEY", os.getenv("OPENCLAW_GATEWAY_TOKEN", "openclaw-local-token"))
        return

    try:
        overrides = json.loads(raw_overrides)
    except json.JSONDecodeError:
        return

    if not isinstance(overrides, dict):
        return

    for key, value in overrides.items():
        if not isinstance(key, str) or not key.startswith("OPENCLAW_"):
            continue
        os.environ[key] = str(value)

    os.environ.setdefault("OPENCLAW_PROXY_API_KEY", os.getenv("OPENCLAW_GATEWAY_TOKEN", "openclaw-local-token"))


def _build_openclaw_agent() -> Agent:
    _apply_openclaw_config_overrides()

    model_id = _get_config_value("openclaw_model") or "openclaw:main"
    instructions = _get_config_value("agent_instructions") or _DEFAULT_ONBOARDING_CONFIG["agent_instructions"]

    return Agent(
        name=_get_config_value("agent_name") or _DEFAULT_ONBOARDING_CONFIG["agent_name"],
        description=_get_config_value("agent_description") or _DEFAULT_ONBOARDING_CONFIG["agent_description"],
        instructions=instructions,
        model=build_openclaw_responses_model(model=model_id),
    )


# Do not remove this method. Deploy flow imports it from main.py.
def create_agency(load_threads_callback=None):
    openclaw_agent = _build_openclaw_agent()
    return Agency(
        openclaw_agent,
        name="OpenClawAgency",
        shared_instructions="shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )


if __name__ == "__main__":
    create_agency().terminal_demo()
