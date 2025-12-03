"""Chat client factory for creating configured client instances."""

from typing import Union
from agent_framework.azure import AzureOpenAIChatClient
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)


def create_chat_client() -> Union[AzureOpenAIChatClient]:
    """
    Create a chat client based on available configuration.

    Returns:
        ChatClient: Configured chat client instance

    Raises:
        ValueError: If no valid configuration is available
    """
    if not config.validate():
        errors = config.get_validation_errors()
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    logger.info("Creating Azure OpenAI chat client")
    return AzureOpenAIChatClient(
        endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_API_KEY,
        deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
    )
