"""Chat client factory for creating configured client instances."""

from typing import Union

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient
from ..config import config
from ..utils.logging import get_logger

logger = get_logger(__name__)


def create_chat_client(agent_name: str) -> Union[OpenAIChatClient, AzureOpenAIChatClient]:
    """
    Create a chat client for the specified agent using the resolved provider config.

    Supports:
    - OpenAI-compatible endpoints (OpenAI, Ollama, LM Studio, etc.)
    - Azure OpenAI (deployment-based)

    Returns:
        ChatClient: Configured chat client instance

    Raises:
        ValueError: If no valid configuration is available
    """
    if not config.validate():
        errors = config.get_validation_errors()
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    agent_config = config.get_agent_llm_config(agent_name)

    if agent_config.provider == "azure":
        logger.info(
            "Creating Azure OpenAI chat client for %s (deployment: %s)",
            agent_name,
            agent_config.deployment_name,
        )
        return AzureOpenAIChatClient(
            endpoint=agent_config.endpoint,
            api_key=agent_config.api_key,
            deployment_name=agent_config.deployment_name,
        )

    logger.info(
        "Creating OpenAI-compatible chat client for %s (model: %s)",
        agent_name,
        agent_config.model_id,
    )
    if agent_config.base_url:
        logger.info("Using custom endpoint: %s", agent_config.base_url)

    client_kwargs = {
        "model_id": agent_config.model_id,
    }

    if agent_config.api_key:
        client_kwargs["api_key"] = agent_config.api_key

    if agent_config.base_url:
        client_kwargs["base_url"] = agent_config.base_url

    return OpenAIChatClient(**client_kwargs)
