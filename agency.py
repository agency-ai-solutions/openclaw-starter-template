from __future__ import annotations

import os

from dotenv import load_dotenv

from agency_swarm import Agency
from openclaw_template_helpers import build_openclaw_agent, load_openclaw_template_config

load_dotenv()
os.environ.setdefault("PORT", "8080")

# Do not remove this method. Deploy flow imports it from main.py.
def create_agency(load_threads_callback=None):
    template_config = load_openclaw_template_config()
    openclaw_assistant = build_openclaw_agent(template_config)
    return Agency(
        openclaw_assistant,
        name="OpenClawAgency",
        load_threads_callback=load_threads_callback,
    )
