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

    # No .env file found, check if likely misconfigured
    has_openai = os.getenv("OPENAI_CHAT_MODEL_ID")
    has_azure = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    if not (has_openai or has_azure):
        print("\nWarning: No .env file found and no LLM configuration detected.")
        print("Please create a .env file in one of these locations:")
        print(f"  - {cwd_env}")
        print(f"  - {home_env}")
        print("\nMinimum environment variables:")
        print("  - LLM_PROVIDER=openai|azure")
        print("  - For OpenAI: OPENAI_CHAT_MODEL_ID plus OPENAI_API_KEY")
        print("  - For Azure: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME")
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
