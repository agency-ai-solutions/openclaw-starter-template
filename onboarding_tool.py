from __future__ import annotations

import os
import pprint

from dotenv import load_dotenv
from pydantic import Field

from agency_swarm.tools import BaseTool

load_dotenv()

try:
    from onboarding_config import config as existing_onboarding_config
except ImportError:
    existing_onboarding_config = {}


class OnboardingTool(BaseTool):
    """Collect deployment settings for the OpenClaw marketplace template."""

    assistant_name: str = Field(..., description="Name shown in chat.")
    assistant_description: str = Field(..., description="What this assistant should help with.")
    assistant_instructions: str | None = Field(
        default=None,
        description="Extra instructions you want to add before deploy.",
        json_schema_extra={"ui:widget": "textarea"},
    )

    def run(self):
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(tool_dir, "onboarding_config.py")

        config = existing_onboarding_config.copy() if isinstance(existing_onboarding_config, dict) else {}
        config.update(self.model_dump())
        python_code = (
            "# Auto-generated onboarding configuration\n\n"
            f"config = {pprint.pformat(config, sort_dicts=True)}\n"
        )

        with open(config_path, "w", encoding="utf-8") as file:
            file.write(python_code)

        return f"Configuration saved at: {config_path}"


if __name__ == "__main__":
    tool = OnboardingTool(
        assistant_name="OpenClaw Assistant",
        assistant_description="A private OpenClaw assistant running on Agent Swarm.",
        assistant_instructions="",
    )
    print(tool.run())
