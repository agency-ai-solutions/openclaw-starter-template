from __future__ import annotations

import os
import shutil
import subprocess

from agency_swarm.integrations.openclaw import OpenClawIntegrationConfig, OpenClawRuntime

from openclaw_template_helpers import apply_openclaw_environment_overrides


def prepare_openclaw_template() -> OpenClawIntegrationConfig:
    apply_openclaw_environment_overrides()
    config = OpenClawIntegrationConfig.from_env()
    OpenClawRuntime(config).ensure_layout()
    _validate_openclaw_config(config)
    return config


def _validate_openclaw_config(config: OpenClawIntegrationConfig) -> None:
    openclaw_bin = shutil.which("openclaw")
    if not openclaw_bin:
        raise RuntimeError("openclaw CLI is required to validate the prepared template config.")

    env = os.environ.copy()
    env["OPENCLAW_CONFIG_PATH"] = str(config.config_path)
    env["OPENCLAW_HOME"] = str(config.home_dir)
    subprocess.run(
        [openclaw_bin, "config", "validate"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


if __name__ == "__main__":
    config = prepare_openclaw_template()
    print(f"Prepared OpenClaw template layout at {config.config_path}")
