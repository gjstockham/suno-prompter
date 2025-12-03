"""Utilities for song idea generation."""

import random
import sys
from utils.logging import get_logger

logger = get_logger(__name__)


def pick_random_idea() -> str:
    """
    Pick a random song idea from the starter ideas file.

    Returns:
        str: A randomly selected song idea

    Raises:
        FileNotFoundError: If starter ideas file doesn't exist
        ValueError: If starter ideas file is empty
    """
    try:
        # Use importlib.resources for Python 3.10+
        if sys.version_info >= (3, 9):
            from importlib.resources import files
            data_path = files("suno_prompter").joinpath("data/starter_ideas.txt")
            content = data_path.read_text()
        else:
            # Fallback for older Python (shouldn't hit this given our >= 3.10 requirement)
            from importlib.resources import read_text
            content = read_text("suno_prompter.data", "starter_ideas.txt")

        ideas = [line.strip() for line in content.splitlines() if line.strip()]

        if not ideas:
            raise ValueError("Starter ideas file is empty")

        # Select random idea
        idea = random.choice(ideas)
        logger.info(f"Selected random idea: {idea}")
        return idea

    except FileNotFoundError:
        logger.error("Starter ideas file not found in package data")
        raise
    except Exception as e:
        logger.error(f"Error picking random idea: {e}")
        raise
