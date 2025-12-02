"""Chat agent implementation using Microsoft Agent Framework (autogen)."""

from typing import Optional, List
import autogen
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)


class ChatAgent:
    """
    Chat agent for processing user messages and generating responses.

    Uses Microsoft autogen framework for multi-agent conversation.
    """

    def __init__(self):
        """Initialize the chat agent with LLM configuration."""
        self.config_list = self._build_config_list()
        self.user_proxy = None
        self.assistant = None
        self._setup_agents()

    def _build_config_list(self) -> List:
        """
        Build the configuration list for autogen agents.

        Returns:
            list: Configuration list for LLM endpoints
        """
        config_list = []

        # Use OpenAI
        if config.OPENAI_API_KEY:
            config_list.append(
                {
                    "model": "gpt-4",
                    "api_key": config.OPENAI_API_KEY,
                }
            )
            logger.info("Using OpenAI API for agent")

        # Use Azure OpenAI (if configured)
        if config.AZURE_OPENAI_API_KEY and config.AZURE_OPENAI_ENDPOINT:
            config_list.append(
                {
                    "model": config.AZURE_OPENAI_MODEL_DEPLOYMENT or "gpt-4",
                    "api_key": config.AZURE_OPENAI_API_KEY,
                    "base_url": config.AZURE_OPENAI_ENDPOINT,
                    "api_type": "azure",
                    "api_version": "2024-02-15-preview",
                }
            )
            logger.info("Using Azure OpenAI API for agent")

        if not config_list:
            raise ValueError("No LLM configuration available")

        return config_list

    def _setup_agents(self):
        """Set up autogen agents for conversation."""
        # User proxy agent (simulates user)
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith(
                "TERMINATE"
            ),
            human_input_mode="NEVER",
            code_execution_config={"use_docker": False},
        )

        # Assistant agent (responds to user)
        system_prompt = """You are a helpful AI assistant for creating music prompts for Suno AI music generation.
Your role is to help users craft detailed, creative prompts that will guide the AI music generator to produce specific musical styles, moods, and characteristics.

When helping with prompts, consider:
- Musical genres and subgenres
- Mood and atmosphere
- Instrumentation and sound qualities
- Tempo and rhythm patterns
- Vocal characteristics (if applicable)
- Production style and quality

Be conversational, creative, and helpful. Ask clarifying questions when needed to better understand the user's vision."""

        self.assistant = autogen.AssistantAgent(
            name="music_prompt_assistant",
            system_message=system_prompt,
            llm_config={"config_list": self.config_list, "temperature": 0.7},
        )

        logger.info("Chat agents initialized successfully")

    def process_message(
        self, user_message: str, message_history: Optional[List] = None
    ) -> str:
        """
        Process a user message and generate a response.

        Args:
            user_message: The message from the user
            message_history: Optional conversation history (for context)

        Returns:
            str: The assistant's response

        Raises:
            Exception: If message processing fails
        """
        try:
            # Prepare conversation context if history provided
            if message_history:
                self._load_conversation_history(message_history)

            # Initiate conversation
            self.user_proxy.initiate_chat(
                self.assistant,
                message=user_message,
                max_consecutive_auto_reply=1,
            )

            # Extract the last message from assistant
            response = self._extract_assistant_response()

            logger.info(f"Message processed: {user_message[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    def _load_conversation_history(self, message_history: List):
        """
        Load conversation history into agent context.

        Args:
            message_history: List of previous messages
        """
        # For this MVP, we include history in the system prompt context
        # In a more sophisticated implementation, this could update agent memory
        if len(message_history) > 1:
            logger.info(f"Loading {len(message_history)} messages from history")

    def _extract_assistant_response(self) -> str:
        """
        Extract the assistant's last response from the conversation.

        Returns:
            str: The assistant's response text
        """
        # Get the last message from the conversation
        if self.user_proxy.chat_messages:
            messages = self.user_proxy.chat_messages.get(self.assistant, [])
            if messages:
                # Return the last assistant message
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        return msg.get("content", "No response generated")

        return "I encountered an issue generating a response. Please try again."
