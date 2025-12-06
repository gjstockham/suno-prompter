"""Compatibility shim to import workflow from the packaged module."""

import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

from suno_prompter.workflows.lyric_workflow import *  # noqa: F401,F403,E402
