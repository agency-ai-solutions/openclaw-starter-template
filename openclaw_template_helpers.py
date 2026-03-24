from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from agency_swarm.agents import OpenClawAgent

load_dotenv()

_DEFAULT_ONBOARDING_CONFIG: dict[str, str] = {
    "assistant_name": "OpenClaw Assistant",
    "assistant_description": "A private OpenClaw assistant running on Agencii.",
    "assistant_instructions": "Handle user tasks and call the right OpenClaw tools when needed.",
    "openclaw_model": "openclaw:main",
    "openclaw_config_overrides_json": '{"OPENCLAW_PROVIDER_MODEL":"openai/gpt-5.4"}',
}

try:
    from onboarding_config import config as onboarding_config
except ImportError:
    onboarding_config = _DEFAULT_ONBOARDING_CONFIG


@dataclass(frozen=True)
class OpenClawTemplateConfig:
    assistant_name: str
    assistant_description: str
    instructions: str


def load_openclaw_template_config() -> OpenClawTemplateConfig:
    _apply_legacy_openclaw_config()
    return OpenClawTemplateConfig(
        assistant_name=_read_config_value("assistant_name", fallback_key="agent_name")
        or _DEFAULT_ONBOARDING_CONFIG["assistant_name"],
        assistant_description=_read_config_value("assistant_description", fallback_key="agent_description")
        or _DEFAULT_ONBOARDING_CONFIG["assistant_description"],
        instructions=_read_config_value("assistant_instructions", fallback_key="agent_instructions")
        or _DEFAULT_ONBOARDING_CONFIG["assistant_instructions"],
    )


def build_openclaw_agent(config: OpenClawTemplateConfig) -> OpenClawAgent:
    return OpenClawAgent(
        name=config.assistant_name,
        description=config.assistant_description,
        instructions=config.instructions,
    )


def _read_config_value(key: str, *, fallback_key: str | None = None) -> str:
    value = onboarding_config.get(key)
    if value in (None, "") and fallback_key is not None:
        value = onboarding_config.get(fallback_key)
    if value in (None, ""):
        value = _DEFAULT_ONBOARDING_CONFIG.get(key, "")
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value)


def _apply_legacy_openclaw_config() -> None:
    legacy_model = _read_config_value("openclaw_model")
    if legacy_model:
        os.environ.setdefault("OPENCLAW_DEFAULT_MODEL", legacy_model)

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
        os.environ.setdefault(key, _as_string(value))


def _as_string(value: Any) -> str:
    return value if isinstance(value, str) else str(value)
