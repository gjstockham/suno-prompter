# Design: Add uvx Distribution Support

## Overview

This design document outlines how to restructure the project for distribution via `uvx` (uv tool run), enabling users to run the app without pre-installing Python.

## Architecture Decision: src Layout

We'll use the modern `src/` layout recommended by Python packaging guides:

```
suno-prompter/
├── src/
│   └── suno_prompter/
│       ├── __init__.py
│       ├── __main__.py      # python -m suno_prompter
│       ├── cli.py           # Entry point for sunoprompt command
│       ├── app.py           # Streamlit application
│       ├── config.py
│       ├── agents/
│       ├── workflows/
│       ├── utils/
│       └── data/
│           └── starter_ideas.txt
├── devui/                    # Keep outside package (dev tool)
├── openspec/                 # Keep outside package (documentation)
├── pyproject.toml
├── README.md
└── .env.example
```

### Rationale

1. **src/ layout prevents accidental imports** - Can't accidentally import from working directory
2. **Clear separation** - Package code vs. project tooling/docs
3. **Standard practice** - Matches modern Python packaging conventions
4. **Easier testing** - Forces tests to use installed package, not source

## CLI Entry Point Design

### cli.py

```python
"""CLI entry point for sunoprompt command."""
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    # Streamlit needs the script path
    app_path = Path(__file__).parent / "app.py"

    # Set up sys.argv for streamlit
    sys.argv = ["streamlit", "run", str(app_path), "--server.headless", "false"]

    # Import and run streamlit CLI
    from streamlit.web import cli as stcli
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
```

### __main__.py

```python
"""Allow running as python -m suno_prompter."""
from suno_prompter.cli import main

if __name__ == "__main__":
    main()
```

## Package Data Handling

### Problem
Data files like `starter_ideas.txt` need to be accessible at runtime.

### Solution
Use `importlib.resources` (Python 3.9+) for reliable package resource access:

```python
# In code that needs data files
from importlib.resources import files

def load_starter_ideas():
    data_dir = files("suno_prompter.data")
    ideas_file = data_dir.joinpath("starter_ideas.txt")
    return ideas_file.read_text().strip().split("\n")
```

### pyproject.toml Configuration

```toml
[tool.setuptools.package-data]
"suno_prompter.data" = ["*.txt"]
```

Or with hatchling:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/suno_prompter"]
```

## Environment Configuration

### Problem
Users need to provide API keys via `.env` file, but the package runs from an isolated environment.

### Solution
Look for `.env` in the current working directory (where user runs the command):

```python
# In config.py
from pathlib import Path
from dotenv import load_dotenv

# Load .env from current working directory
env_path = Path.cwd() / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Also check user's home directory
    home_env = Path.home() / ".suno-prompter" / ".env"
    if home_env.exists():
        load_dotenv(home_env)
```

## pyproject.toml Structure

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "suno-prompter"
version = "0.1.0"
description = "AI-powered music prompt generator for Suno"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
dependencies = [
    "streamlit>=1.32.0",
    "agent-framework",
    "python-dotenv>=1.0.0",
    "nest-asyncio>=1.5.0",
]

[project.scripts]
suno-prompter = "suno_prompter.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/suno_prompter"]
```

## Import Path Updates

All imports need updating from flat structure to package structure:

| Old Import | New Import |
|------------|------------|
| `from agents import ...` | `from suno_prompter.agents import ...` |
| `from utils.logging import ...` | `from suno_prompter.utils.logging import ...` |
| `from config import ...` | `from suno_prompter.config import ...` |
| `from workflows import ...` | `from suno_prompter.workflows import ...` |

## User Experience

### First-time Setup

```bash
# 1. Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create config directory and .env
mkdir -p ~/.suno-prompter
cp .env.example ~/.suno-prompter/.env
# Edit ~/.suno-prompter/.env with API keys

# 3. Run the app
uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter
```

### Subsequent Runs

```bash
# Just run - uv caches the package
uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter
```

## Trade-offs

### Advantages
- Single-command installation (just `uv`)
- No Python version management for users
- Isolated environment prevents conflicts
- Works on Linux, macOS, Windows

### Disadvantages
- Requires users to install `uv` (though this is quick)
- `.env` configuration still required for API keys
- Slightly more complex project structure
- Development workflow changes (must use `pip install -e .`)
