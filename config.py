"""Configuration management for the Suno Prompter application."""

import os
from typing import Optional, List
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Azure OpenAI Configuration (optional)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_MODEL_DEPLOYMENT: Optional[str] = os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT")

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
        # Check if at least one API key source is configured
        has_openai = bool(cls.OPENAI_API_KEY.strip())
        has_azure = bool(cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT)

        if not (has_openai or has_azure):
            return False

        return True

    @classmethod
    def get_validation_errors(cls) -> List[str]:
        """
        Get a list of validation errors.

        Returns:
            list: List of error messages, empty if configuration is valid
        """
        errors = []

        has_openai = bool(cls.OPENAI_API_KEY.strip())
        has_azure = bool(cls.AZURE_OPENAI_API_KEY and cls.AZURE_OPENAI_ENDPOINT)

        if not (has_openai or has_azure):
            errors.append("No API key configured. Set OPENAI_API_KEY or AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT")

        if has_azure and not cls.AZURE_OPENAI_MODEL_DEPLOYMENT:
            errors.append("AZURE_OPENAI_MODEL_DEPLOYMENT must be set when using Azure OpenAI")

        return errors


# Export configuration instance
config = Config()
