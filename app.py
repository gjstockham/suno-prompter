"""Main Streamlit application for the Suno Prompter."""

import streamlit as st
from config import config
from utils.logging import get_logger
from workflows import LyricWorkflow
from workflows.lyric_workflow import WorkflowInputs, WorkflowStatus

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
    """Initialize Streamlit session state for workflow."""
    if "workflow" not in st.session_state:
        st.session_state.workflow = {
            "inputs": {
                "artists": "",
                "songs": "",
                "guidance": "",
            },
            "outputs": {
                "template": None,
                "lyrics": None,
                "reviewed": None,
                "arranged": None,
            },
            "status": "idle",
            "error": None,
        }
    if "workflow_instance" not in st.session_state:
        st.session_state.workflow_instance = None


def validate_configuration():
    """Validate that the application configuration is correct."""
    if not config.validate():
        st.error("Configuration Error")
        error_message = """
The application requires API key configuration. Please:

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to `.env`
3. Restart the application

For Azure OpenAI, set:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_MODEL_DEPLOYMENT
        """
        st.error(error_message)
        st.stop()


def initialize_workflow():
    """Initialize the workflow orchestrator."""
    if st.session_state.workflow_instance is None:
        try:
            st.session_state.workflow_instance = LyricWorkflow()
            logger.info("Workflow initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize workflow: {str(e)}")
            logger.error(f"Workflow initialization error: {e}")
            st.stop()


def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        st.title("Suno Prompter")
        st.markdown("---")
        st.markdown("### Settings")

        # Clear workflow button
        if st.button("Clear Workflow", use_container_width=True):
            st.session_state.workflow = {
                "inputs": {
                    "artists": "",
                    "songs": "",
                    "guidance": "",
                },
                "outputs": {
                    "template": None,
                    "lyrics": None,
                    "reviewed": None,
                    "arranged": None,
                },
                "status": "idle",
                "error": None,
            }
            st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "Create perfect prompts for Suno music generation using AI agents."
        )


def render_workflow_form():
    """Render the workflow input form."""
    st.subheader("Create Lyric Blueprint")
    st.markdown(
        "Enter song references below. The AI will analyze the lyrical patterns "
        "and generate a detailed blueprint."
    )

    # Input fields
    artists = st.text_input(
        "Artist(s)",
        value=st.session_state.workflow["inputs"]["artists"],
        placeholder="e.g., Taylor Swift, Ed Sheeran",
        help="Enter one or more artists whose style you want to analyze",
    )

    songs = st.text_input(
        "Song(s)",
        value=st.session_state.workflow["inputs"]["songs"],
        placeholder="e.g., Shake It Off, Shape of You",
        help="Enter specific songs to analyze",
    )

    guidance = st.text_area(
        "Other guidance",
        value=st.session_state.workflow["inputs"]["guidance"],
        placeholder="Any additional instructions or style preferences...",
        help="Provide any additional context or requirements",
        height=100,
    )

    # Update session state with current values
    st.session_state.workflow["inputs"]["artists"] = artists
    st.session_state.workflow["inputs"]["songs"] = songs
    st.session_state.workflow["inputs"]["guidance"] = guidance

    # Generate button
    if st.button("Generate Blueprint", type="primary", use_container_width=True):
        run_workflow()


def run_workflow():
    """Execute the workflow pipeline."""
    inputs = WorkflowInputs(
        artists=st.session_state.workflow["inputs"]["artists"],
        songs=st.session_state.workflow["inputs"]["songs"],
        guidance=st.session_state.workflow["inputs"]["guidance"],
    )

    # Validate at least one input is provided
    if not any([inputs.artists.strip(), inputs.songs.strip(), inputs.guidance.strip()]):
        st.error("Please provide at least one of: Artist(s), Song(s), or guidance")
        return

    # Show progress
    with st.spinner("Generating lyric blueprint..."):
        try:
            result = st.session_state.workflow_instance.run(inputs)

            # Update session state with results
            st.session_state.workflow["status"] = result.status.value
            st.session_state.workflow["outputs"]["template"] = result.outputs.template
            st.session_state.workflow["error"] = result.error

            if result.status == WorkflowStatus.ERROR:
                logger.error(f"Workflow failed: {result.error}")
            else:
                logger.info("Workflow completed successfully")

        except Exception as e:
            st.session_state.workflow["status"] = "error"
            st.session_state.workflow["error"] = str(e)
            logger.error(f"Workflow execution error: {e}")

    st.rerun()


def render_output():
    """Render the workflow output."""
    status = st.session_state.workflow["status"]
    error = st.session_state.workflow["error"]
    template = st.session_state.workflow["outputs"]["template"]

    if status == "error" and error:
        st.error(f"Error: {error}")
    elif status == "complete" and template:
        st.markdown("---")
        st.subheader("Lyric Blueprint")
        st.markdown(template)


def main():
    """Main application entry point."""
    initialize_app()
    initialize_session_state()
    validate_configuration()
    initialize_workflow()

    # Render UI
    render_sidebar()

    st.title("Suno Prompter")
    st.markdown(
        "Create amazing music prompts for Suno AI generation using intelligent lyric analysis."
    )
    st.markdown("---")

    render_workflow_form()
    render_output()


if __name__ == "__main__":
    main()
