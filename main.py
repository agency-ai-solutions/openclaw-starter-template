import logging
import os

import uvicorn
from dotenv import load_dotenv

from agency import create_agency
from agency_swarm.integrations.fastapi import run_fastapi
from agency_swarm.integrations.openclaw import attach_openclaw_to_fastapi

load_dotenv()
logging.basicConfig(level=logging.INFO)


def _configure_openclaw_proxy_env() -> None:
    port = os.getenv("PORT", "8080")
    os.environ.setdefault("OPENCLAW_PROXY_BASE_URL", f"http://127.0.0.1:{port}/openclaw/v1")
    os.environ.setdefault("OPENCLAW_PROXY_API_KEY", os.getenv("OPENCLAW_GATEWAY_TOKEN", "openclaw-local-token"))


def create_app():
    _configure_openclaw_proxy_env()

    app = run_fastapi(
        agencies={"openclaw": create_agency},
        app_token_env="APP_TOKEN",
        return_app=True,
        enable_logging=True,
    )
    if app is None:
        raise RuntimeError("FastAPI app failed to start")

    attach_openclaw_to_fastapi(app)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
