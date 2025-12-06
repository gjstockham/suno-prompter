"""Workflow orchestration for the Suno Prompter application (compat shim)."""

import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

from suno_prompter.workflows import LyricWorkflow  # noqa: E402

__all__ = ["LyricWorkflow"]
