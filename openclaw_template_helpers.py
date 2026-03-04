from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from agency_swarm import Agent
from agency_swarm.integrations.openclaw import build_openclaw_responses_model

load_dotenv()

_DEFAULT_ONBOARDING_CONFIG: dict[str, str] = {
    "agent_name": "OpenClaw Agent",
    "agent_description": "Agent powered by an OpenClaw Responses backend.",
    "openclaw_model": "openclaw:main",
    "agent_instructions": "Handle user tasks and call tools when needed.",
    "openclaw_config_overrides_json": '{"OPENCLAW_PROVIDER_MODEL":"openai-codex/gpt-5.2"}',
}

try:
    from onboarding_config import config as onboarding_config
except ImportError:
    onboarding_config = _DEFAULT_ONBOARDING_CONFIG


@dataclass(frozen=True)
class OpenClawTemplateConfig:
    agent_name: str
    agent_description: str
    model_id: str
    instructions: str


def load_openclaw_template_config() -> OpenClawTemplateConfig:
    _apply_openclaw_config_overrides()
    _ensure_proxy_api_key()
    return OpenClawTemplateConfig(
        agent_name=_read_config_value("agent_name") or _DEFAULT_ONBOARDING_CONFIG["agent_name"],
        agent_description=_read_config_value("agent_description") or _DEFAULT_ONBOARDING_CONFIG["agent_description"],
        model_id=_read_config_value("openclaw_model") or _DEFAULT_ONBOARDING_CONFIG["openclaw_model"],
        instructions=_read_config_value("agent_instructions") or _DEFAULT_ONBOARDING_CONFIG["agent_instructions"],
    )


def build_openclaw_agent(config: OpenClawTemplateConfig) -> Agent:
    base_url = os.getenv("OPENCLAW_PROXY_BASE_URL")
    if not base_url:
        base_url = f"http://127.0.0.1:{os.getenv('PORT', '8080')}/openclaw/v1"

    return Agent(
        name=config.agent_name,
        description=config.agent_description,
        instructions=config.instructions,
        model=build_openclaw_responses_model(model=config.model_id, base_url=base_url),
    )


def _read_config_value(key: str) -> str:
    value = onboarding_config.get(key, _DEFAULT_ONBOARDING_CONFIG.get(key, ""))
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def _apply_openclaw_config_overrides() -> None:
    raw_overrides = _read_config_value("openclaw_config_overrides_json")
    if not raw_overrides:
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
        os.environ[key] = _as_string(value)


def _ensure_proxy_api_key() -> None:
    # The local proxy is protected by APP_TOKEN. Gateway token is only a fallback
    # for setups where APP_TOKEN is intentionally unset.
    proxy_api_key = os.getenv("APP_TOKEN")
    if not proxy_api_key:
        proxy_api_key = os.getenv("OPENCLAW_GATEWAY_TOKEN")
    if proxy_api_key:
        os.environ.setdefault("OPENCLAW_PROXY_API_KEY", proxy_api_key)


def _as_string(value: Any) -> str:
    return value if isinstance(value, str) else str(value)
