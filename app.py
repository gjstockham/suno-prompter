"""Main Streamlit application for the Suno Prompter."""

import streamlit as st
from config import config
from utils.logging import get_logger
from agents import ChatAgent

logger = get_logger(__name__)


def initialize_app():
    """Initialize the Streamlit app configuration and state."""
    st.set_page_config(
        page_title="Suno Prompter",
        page_icon="🎵",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def initialize_session_state():
    """Initialize Streamlit session state for conversation history."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False


def validate_configuration():
    """Validate that the application configuration is correct."""
    if not config.validate():
        st.error("❌ Configuration Error")
        st.error_details = """
        The application requires API key configuration. Please:

        1. Copy `.env.example` to `.env`
        2. Add your OpenAI API key to `.env`
        3. Restart the application

        For Azure OpenAI, set:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_MODEL_DEPLOYMENT
        """
        st.error(st.error_details)
        st.stop()


def initialize_agent():
    """Initialize the chat agent."""
    if not st.session_state.agent_initialized:
        try:
            st.session_state.agent = ChatAgent()
            st.session_state.agent_initialized = True
            logger.info("Chat agent initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize chat agent: {str(e)}")
            logger.error(f"Agent initialization error: {e}")
            st.stop()


def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        st.title("🎵 Suno Prompter")
        st.markdown("---")
        st.markdown("### Settings")

        # Clear conversation button
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "Create perfect prompts for Suno music generation using AI agents."
        )


def render_messages():
    """Render the conversation history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    """Handle user message input and agent processing."""
    if prompt := st.chat_input("Enter your message..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process with agent and display response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.process_message(
                        prompt, st.session_state.messages
                    )
                    st.markdown(response)

                    # Add agent response to history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                    logger.info("Message processed successfully")
                except Exception as e:
                    error_msg = f"Error processing message: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"Message processing error: {e}")


def main():
    """Main application entry point."""
    initialize_app()
    initialize_session_state()
    validate_configuration()
    initialize_agent()

    # Render UI
    render_sidebar()

    st.title("🎵 Suno Prompter")
    st.markdown(
        "Welcome! I help you create amazing music prompts for Suno AI generation."
    )
    st.markdown("---")

    render_messages()
    handle_user_input()


if __name__ == "__main__":
    main()
