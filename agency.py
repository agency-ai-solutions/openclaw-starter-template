from __future__ import annotations

from dotenv import load_dotenv

from agency_swarm import Agency
from openclaw_template_helpers import build_openclaw_agent, load_openclaw_template_config

load_dotenv()

# Do not remove this method. Deploy flow imports it from main.py.
def create_agency(load_threads_callback=None):
    template_config = load_openclaw_template_config()
    openclaw_agent = build_openclaw_agent(template_config)
    return Agency(
        openclaw_agent,
        name="OpenClawAgency",
        load_threads_callback=load_threads_callback,
    )


if __name__ == "__main__":
    create_agency().terminal_demo()
