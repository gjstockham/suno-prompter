"""Utilities for song idea generation."""

import random
from pathlib import Path
from .logging import get_logger

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
        # Load ideas from packaged data in backend/services/data
        data_path = Path(__file__).resolve().parent.parent / "data" / "starter_ideas.txt"
        content = data_path.read_text()

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
