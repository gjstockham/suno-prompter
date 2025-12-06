"""Wrapper to run the packaged Suno Prompter app."""

import sys
from pathlib import Path


# Ensure local src/ is importable when running from repo root
ROOT = Path(__file__).parent
SRC_PATH = ROOT / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

# Load environment variables (mirrors CLI behavior)
try:
    from suno_prompter.cli import load_environment  # type: ignore  # noqa: E402

    load_environment()
except Exception:
    # Best-effort; fall through if CLI loader unavailable
    pass

from suno_prompter.app import main  # noqa: E402


if __name__ == "__main__":
    main()
