import logging
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from agency import create_agency
from agency_swarm.integrations.fastapi import run_fastapi
from agency_swarm.integrations.openclaw import attach_openclaw_to_fastapi
from openclaw_runtime_bootstrap import ensure_openclaw_runtime
from openclaw_template_helpers import apply_openclaw_environment_overrides

load_dotenv()
logging.basicConfig(level=logging.INFO)


def create_app():
    apply_openclaw_environment_overrides()
    ensure_openclaw_runtime()
    port = int(os.getenv("PORT", "8080"))
    logs_dir = os.getenv("AGENCY_LOGS_DIR")
    if not logs_dir:
        openclaw_home = Path(os.getenv("OPENCLAW_HOME", Path.cwd() / ".data" / "openclaw"))
        logs_dir = str(openclaw_home / "logs" / "activity-logs")
    app = run_fastapi(
        agencies={"openclaw": create_agency},
        port=port,
        app_token_env="APP_TOKEN",
        return_app=True,
        enable_logging=True,
        logs_dir=logs_dir,
    )
    if app is None:
        raise RuntimeError("FastAPI app failed to start")

    attach_openclaw_to_fastapi(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")), ws="websockets-sansio")
