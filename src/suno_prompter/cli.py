"""CLI entry point for Suno Prompter."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables from .env files in predictable locations.

    Priority order:
    1. Current working directory (./.env)
    2. Home directory (~/.suno-prompter/.env)
    3. Environment variables already set
    """
    # Check current directory first
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        print(f"Loading environment from: {cwd_env}")
        load_dotenv(cwd_env)
        return

    # Check home directory
    home_env = Path.home() / ".suno-prompter" / ".env"
    if home_env.exists():
        print(f"Loading environment from: {home_env}")
        load_dotenv(home_env)
        return

    # No .env file found, check if required vars are already set
    if not os.getenv("OPENAI_CHAT_MODEL_ID"):
        print("\nWarning: No .env file found and OPENAI_CHAT_MODEL_ID not set.")
        print("Please create a .env file in one of these locations:")
        print(f"  - {cwd_env}")
        print(f"  - {home_env}")
        print("\nRequired environment variables:")
        print("  - OPENAI_CHAT_MODEL_ID (e.g., 'gpt-4', 'llama3')")
        print("  - OPENAI_API_KEY (for OpenAI API)")
        print("  - OPENAI_BASE_URL (optional, for custom endpoints)")
        print()


def main():
    """Main CLI entry point - launches Streamlit app."""
    # Load environment variables first
    load_environment()

    # Import streamlit and run the app
    # We use streamlit.web.cli to run the app programmatically
    from streamlit.web import cli as st_cli

    # Get the path to app.py relative to this file
    app_path = Path(__file__).parent / "app.py"

    # Run streamlit with the app file
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(st_cli.main())


if __name__ == "__main__":
    main()
