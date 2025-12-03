"""Configuration management for the Suno Prompter application."""

import os
from typing import Optional, List
from dotenv import load_dotenv


# NOTE: dotenv loading is handled by cli.py
# This allows flexibility in .env file locations


class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI-compatible API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")
    OPENAI_CHAT_MODEL_ID: Optional[str] = os.getenv("OPENAI_CHAT_MODEL_ID")

    # Application Settings
    DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # OPENAI_API_KEY is optional if using a local endpoint that doesn't require auth
        # But OPENAI_CHAT_MODEL_ID is always required
        return bool(cls.OPENAI_CHAT_MODEL_ID)

    @classmethod
    def get_validation_errors(cls) -> List[str]:
        """
        Get a list of validation errors.

        Returns:
            list: List of error messages, empty if configuration is valid
        """
        errors = []

        if not cls.OPENAI_CHAT_MODEL_ID:
            errors.append("OPENAI_CHAT_MODEL_ID must be set (e.g., 'gpt-4', 'llama3')")

        # Warn if neither API key nor base URL is set (likely misconfiguration)
        if not cls.OPENAI_API_KEY and not cls.OPENAI_BASE_URL:
            errors.append(
                "Either OPENAI_API_KEY or OPENAI_BASE_URL should be configured. "
                "Set OPENAI_API_KEY for OpenAI API, or OPENAI_BASE_URL for custom endpoints."
            )

        return errors


# Export configuration instance
config = Config()
