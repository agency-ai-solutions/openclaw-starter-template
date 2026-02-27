from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from pydantic import Field

from agency_swarm.tools import BaseTool

load_dotenv()


class OnboardingTool(BaseTool):
    """Collect deployment settings for the OpenClaw marketplace template."""

    agent_name: str = Field(..., description="Name of the OpenClaw agent shown to users.")
    agent_description: str = Field(..., description="Short description of what this agent should do.")
    openclaw_model: str = Field(
        default="openclaw:main",
        description="OpenClaw model id used by the agent.",
    )
    agent_instructions: str | None = Field(
        default=None,
        description="Optional extra instructions for the agent.",
        json_schema_extra={"ui:widget": "textarea"},
    )
    openclaw_config_overrides_json: str | None = Field(
        default=None,
        description="Optional JSON object with OPENCLAW_* env overrides.",
        json_schema_extra={"ui:widget": "textarea"},
    )

    def run(self):
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(tool_dir, "onboarding_config.py")

        config = self.model_dump()
        python_code = (
            "# Auto-generated onboarding configuration\n\n"
            f"config = {json.dumps(config, indent=4, ensure_ascii=True)}\n"
        )

        with open(config_path, "w", encoding="utf-8") as file:
            file.write(python_code)

        return f"Configuration saved at: {config_path}"


if __name__ == "__main__":
    tool = OnboardingTool(
        agent_name="OpenClaw Agent",
        agent_description="Automates tasks through OpenClaw.",
        openclaw_model="openclaw:main",
        agent_instructions="",
        openclaw_config_overrides_json="",
    )
    print(tool.run())
