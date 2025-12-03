"""Utilities for song idea generation."""

import random
import os
from utils.logging import get_logger

logger = get_logger(__name__)

# Path to starter ideas file
STARTER_IDEAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "starter_ideas.txt")


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
        # Read all ideas from file
        with open(STARTER_IDEAS_FILE, "r") as f:
            ideas = [line.strip() for line in f if line.strip()]

        if not ideas:
            raise ValueError("Starter ideas file is empty")

        # Select random idea
        idea = random.choice(ideas)
        logger.info(f"Selected random idea: {idea}")
        return idea

    except FileNotFoundError:
        logger.error(f"Starter ideas file not found: {STARTER_IDEAS_FILE}")
        raise
    except Exception as e:
        logger.error(f"Error picking random idea: {e}")
        raise
