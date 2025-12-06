"""Configuration management for the Suno Prompter application."""

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional


# NOTE: dotenv loading is handled by cli.py
# This allows flexibility in .env file locations


SUPPORTED_PROVIDERS = {"openai", "azure"}

# Map logical agent names to env var prefixes for overrides
AGENT_ENV_PREFIXES: Dict[str, str] = {
    "lyric_template": "TEMPLATE",
    "lyric_writer": "WRITER",
    "lyric_reviewer": "REVIEWER",
    "suno_producer": "PRODUCER",
}


@dataclass
class LLMConfig:
    """Resolved configuration for a specific agent/provider combination."""

    provider: str
    model_id: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    deployment_name: Optional[str] = None


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        # Defaults
        self.default_provider = (os.getenv("LLM_PROVIDER") or "openai").lower()

        # OpenAI-compatible API configuration
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")
        self.openai_chat_model_id: Optional[str] = os.getenv("OPENAI_CHAT_MODEL_ID")

        # Azure OpenAI configuration
        self.azure_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        # Optional: Some Azure setups also expose a model ID
        self.azure_model_id: Optional[str] = os.getenv("AZURE_OPENAI_MODEL_ID")

        # Application settings
        self.DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def _normalize_provider(self, provider: str) -> str:
        provider_normalized = provider.lower()
        if provider_normalized not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider '{provider}'. Supported providers: {sorted(SUPPORTED_PROVIDERS)}")
        return provider_normalized

    def _get_agent_override(self, agent_name: str) -> Dict[str, Optional[str]]:
        if agent_name not in AGENT_ENV_PREFIXES:
            raise ValueError(f"Unknown agent '{agent_name}' - expected one of {sorted(AGENT_ENV_PREFIXES)}")

        prefix = AGENT_ENV_PREFIXES[agent_name]
        return {
            "provider": os.getenv(f"{prefix}_LLM_PROVIDER"),
            "model_id": os.getenv(f"{prefix}_CHAT_MODEL_ID"),
            # Azure-specific override to allow different deployments per agent
            "deployment_name": os.getenv(f"{prefix}_AZURE_DEPLOYMENT_NAME"),
        }

    @lru_cache(maxsize=None)
    def get_agent_llm_config(self, agent_name: str) -> LLMConfig:
        """Return the resolved LLM config for the given agent."""

        override = self._get_agent_override(agent_name)
        provider = self._normalize_provider(override["provider"] or self.default_provider)

        if provider == "azure":
            deployment_name = override["deployment_name"] or self.azure_deployment_name
            return LLMConfig(
                provider="azure",
                api_key=self.azure_api_key,
                endpoint=self.azure_endpoint,
                deployment_name=deployment_name,
                model_id=override["model_id"] or self.azure_model_id,
            )

        # Default: OpenAI-compatible
        return LLMConfig(
            provider="openai",
            model_id=override["model_id"] or self.openai_chat_model_id,
            base_url=self.openai_base_url,
            api_key=self.openai_api_key,
        )

    def validate(self) -> bool:
        """Validate that required configuration is present for all agents."""

        return not self.get_validation_errors()

    def get_validation_errors(self) -> List[str]:
        """Get a list of validation errors across all agents."""

        errors: List[str] = []
        seen: set[str] = set()

        for agent_name in AGENT_ENV_PREFIXES:
            try:
                agent_config = self.get_agent_llm_config(agent_name)
            except ValueError as exc:  # unknown provider/agent
                errors.append(str(exc))
                continue

            prefix = AGENT_ENV_PREFIXES[agent_name]

            if agent_config.provider == "azure":
                if not agent_config.endpoint:
                    seen.add("AZURE_OPENAI_ENDPOINT must be set for Azure provider")
                if not agent_config.api_key:
                    seen.add("AZURE_OPENAI_API_KEY must be set for Azure provider")
                if not agent_config.deployment_name:
                    seen.add(
                        f"Azure deployment name missing for {agent_name}. "
                        f"Set {prefix}_AZURE_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT_NAME."
                    )
            elif agent_config.provider == "openai":
                if not agent_config.model_id:
                    seen.add(
                        f"Model ID missing for {agent_name}. "
                        f"Set {prefix}_CHAT_MODEL_ID or OPENAI_CHAT_MODEL_ID."
                    )
                if not agent_config.api_key and not agent_config.base_url:
                    seen.add(
                        "Either OPENAI_API_KEY or OPENAI_BASE_URL should be configured. "
                        "Set OPENAI_API_KEY for OpenAI API, or OPENAI_BASE_URL for custom endpoints."
                    )
            else:
                errors.append(f"Unsupported provider '{agent_config.provider}' for {agent_name}")

        errors.extend(sorted(seen))
        return errors


# Export configuration instance
config = Config()
