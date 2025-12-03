"""
Agent instances for DevUI debugging.

Run with: python devui/agents.py
This exposes individual agents for debugging in the DevUI web interface.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework.devui import serve
from agents import (
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
