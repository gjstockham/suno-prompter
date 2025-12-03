"""Chat client factory for creating configured client instances."""

from typing import Union
from agent_framework.openai import OpenAIChatClient
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)


def create_chat_client() -> Union[OpenAIChatClient]:
    """
    Create a chat client based on available configuration.

    Supports OpenAI-compatible endpoints including:
    - Official OpenAI API (api.openai.com)
    - Custom endpoints (Ollama, LM Studio, etc.)

    Returns:
        ChatClient: Configured chat client instance

    Raises:
        ValueError: If no valid configuration is available
    """
    if not config.validate():
        errors = config.get_validation_errors()
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    logger.info(f"Creating OpenAI chat client for model: {config.OPENAI_CHAT_MODEL_ID}")
    if config.OPENAI_BASE_URL:
        logger.info(f"Using custom endpoint: {config.OPENAI_BASE_URL}")

    client_kwargs = {
        "model_id": config.OPENAI_CHAT_MODEL_ID,
    }

    if config.OPENAI_API_KEY:
        client_kwargs["api_key"] = config.OPENAI_API_KEY

    if config.OPENAI_BASE_URL:
        client_kwargs["base_url"] = config.OPENAI_BASE_URL

    return OpenAIChatClient(**client_kwargs)
