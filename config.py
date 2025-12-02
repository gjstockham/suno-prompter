"""Configuration management for the Suno Prompter application."""

import os
from typing import Optional, List
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

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
        has_azure = bool(
            cls.AZURE_OPENAI_API_KEY
            and cls.AZURE_OPENAI_ENDPOINT
            and cls.AZURE_OPENAI_DEPLOYMENT_NAME
        )
        return has_azure

    @classmethod
    def get_validation_errors(cls) -> List[str]:
        """
        Get a list of validation errors.

        Returns:
            list: List of error messages, empty if configuration is valid
        """
        errors = []

        if not cls.AZURE_OPENAI_ENDPOINT:
            errors.append("AZURE_OPENAI_ENDPOINT must be set")
        if not cls.AZURE_OPENAI_API_KEY:
            errors.append("AZURE_OPENAI_API_KEY must be set")
        if not cls.AZURE_OPENAI_DEPLOYMENT_NAME:
            errors.append("AZURE_OPENAI_DEPLOYMENT_NAME must be set")

        return errors


# Export configuration instance
config = Config()
