"""Chat agent implementation using Microsoft Agent Framework."""

import asyncio
from typing import Optional, List
from agent_framework import ChatAgent as FrameworkChatAgent
from agent_framework.openai import OpenAIChatClient
from agent_framework.azure import AzureOpenAIChatClient
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)


class ChatAgent:
    """
    Chat agent for processing user messages and generating responses.

    Uses Microsoft Agent Framework for intelligent agent capabilities.
    """

    def __init__(self):
        """Initialize the chat agent with appropriate chat client."""
        self.agent = None
        self.thread = None
        self._setup_agent()

    def _setup_agent(self):
        """Set up the agent with configured chat client."""
        try:
            chat_client = self._create_chat_client()

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

            self.agent = FrameworkChatAgent(
                chat_client=chat_client,
                instructions=system_prompt,
                name="SunoPromptAssistant",
            )

            # Create a new thread for conversation
            self.thread = self.agent.get_new_thread()

            logger.info("Chat agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing chat agent: {e}")
            raise

    def _create_chat_client(self):
        """
        Create a chat client based on available configuration.

        Returns:
            ChatClient: Configured chat client instance

        Raises:
            ValueError: If no valid configuration is available
        """
        # Prefer Azure OpenAI if configured
        if config.AZURE_OPENAI_API_KEY and config.AZURE_OPENAI_ENDPOINT:
            logger.info("Using Azure OpenAI chat client")
            return AzureOpenAIChatClient(
                endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_key=config.AZURE_OPENAI_API_KEY,
                model_id=config.AZURE_OPENAI_MODEL_DEPLOYMENT or "gpt-4o-mini",
            )

        # Fall back to OpenAI
        if config.OPENAI_API_KEY:
            logger.info("Using OpenAI chat client")
            return OpenAIChatClient(
                model_id="gpt-4o-mini",
                api_key=config.OPENAI_API_KEY,
            )

        raise ValueError("No valid API key configuration found")

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
            # Run the agent asynchronously and get the response
            response = asyncio.run(self._run_agent_async(user_message))
            logger.info(f"Message processed: {user_message[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    async def _run_agent_async(self, user_message: str) -> str:
        """
        Run the agent asynchronously.

        Args:
            user_message: The message to process

        Returns:
            str: The agent's response text
        """
        try:
            response = await self.agent.run(user_message, thread=self.thread)
            return response.text or "No response generated"
        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise

    def get_conversation_history(self) -> List:
        """
        Get the current conversation history.

        Returns:
            List: The conversation history from the thread
        """
        if self.thread:
            return self.thread.messages if hasattr(self.thread, "messages") else []
        return []

    def clear_history(self):
        """Clear the conversation history by creating a new thread."""
        if self.agent:
            self.thread = self.agent.get_new_thread()
            logger.info("Conversation history cleared")
