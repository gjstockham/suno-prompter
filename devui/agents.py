"""
Agent instances for DevUI debugging.

Run with: python devui/agents.py
This exposes individual agents for debugging in the DevUI web interface.
"""

import sys
from pathlib import Path


# Add src/ to path so we can import the packaged agents when running from repo root
ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

from agent_framework.devui import serve
from suno_prompter.agents import (
    create_lyric_template_agent,
    create_lyric_writer_agent,
    create_lyric_reviewer_agent,
    create_suno_producer_agent,
)


def main():
    """Start DevUI with all agents registered."""
    # Create agent instances
    agents = [
        create_lyric_template_agent(),
        create_lyric_writer_agent(),
        create_lyric_reviewer_agent(),
        create_suno_producer_agent(),
    ]

    print("Starting DevUI with agents:")
    for agent in agents:
        print(f"  - {agent.name}")

    # Start DevUI server with agents
    serve(
        entities=agents,
        port=8090,
        auto_open=False,
    )


if __name__ == "__main__":
    main()
