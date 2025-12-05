"""Main Streamlit application for the Suno Prompter (Framework-based)."""

import streamlit as st
import asyncio
from config import config
from utils.logging import get_logger
from utils.ideas import pick_random_idea
from src.suno_prompter.workflows.builder import build_suno_workflow
from src.suno_prompter.workflows.types import SongIdeaRequest, LyricApprovalRequest, WorkflowOutput
from src.suno_prompter.adapters.streamlit_adapter import StreamlitWorkflowAdapter
from agents import (
    create_lyric_template_agent,
    create_lyric_writer_agent,
    create_lyric_reviewer_agent,
    create_suno_producer_agent,
)

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
    if "workflow_adapter" not in st.session_state:
        st.session_state.workflow_adapter = None

    if "workflow_inputs" not in st.session_state:
        st.session_state.workflow_inputs = {
            "artists": "",
            "songs": "",
            "guidance": "",
        }


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
    if st.session_state.workflow_adapter is None:
        try:
            # Create agents
            template_agent = create_lyric_template_agent()
            writer_agent = create_lyric_writer_agent()
            reviewer_agent = create_lyric_reviewer_agent()
            producer_agent = create_suno_producer_agent()

            # Build workflow with checkpointing
            workflow, checkpoint_storage = build_suno_workflow(
                template_agent=template_agent,
                writer_agent=writer_agent,
                reviewer_agent=reviewer_agent,
                producer_agent=producer_agent,
                max_iterations=3,
            )

            # Wrap in adapter with checkpoint storage
            st.session_state.workflow_adapter = StreamlitWorkflowAdapter(
                workflow, checkpoint_storage
            )
            logger.info("Workflow initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize workflow: {str(e)}")
            logger.error(f"Workflow initialization error: {e}")
            import traceback
            traceback.print_exc()
            st.stop()


def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        st.title("Suno Prompter")
        st.markdown("---")
        st.markdown("### Settings")

        # Clear workflow button
        if st.button("Clear Workflow", use_container_width=True):
            if st.session_state.workflow_adapter:
                st.session_state.workflow_adapter.reset()
            st.session_state.workflow_inputs = {
                "artists": "",
                "songs": "",
                "guidance": "",
            }
            st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "Create perfect prompts for Suno music generation using AI agents."
        )


def render_workflow_form():
    """Render the workflow input form."""
    adapter = st.session_state.workflow_adapter

    # Only show form if workflow is idle
    if adapter and adapter.get_status() != "idle":
        return

    st.subheader("Create Lyric Blueprint")
    st.markdown(
        "Enter song references below. The AI will analyze the lyrical patterns "
        "and generate a detailed blueprint."
    )

    # Input fields
    artists = st.text_input(
        "Artist(s)",
        value=st.session_state.workflow_inputs["artists"],
        placeholder="e.g., Taylor Swift, Ed Sheeran",
        help="Enter one or more artists whose style you want to analyze",
    )

    songs = st.text_input(
        "Song(s)",
        value=st.session_state.workflow_inputs["songs"],
        placeholder="e.g., Shake It Off, Shape of You",
        help="Enter specific songs to analyze",
    )

    guidance = st.text_area(
        "Other guidance",
        value=st.session_state.workflow_inputs["guidance"],
        placeholder="Any additional instructions or style preferences...",
        help="Provide any additional context or requirements",
        height=100,
    )

    # Update session state with current values
    st.session_state.workflow_inputs["artists"] = artists
    st.session_state.workflow_inputs["songs"] = songs
    st.session_state.workflow_inputs["guidance"] = guidance

    # Generate button
    if st.button("Generate Blueprint", type="primary", use_container_width=True):
        run_workflow()


def render_hitl_requests():
    """Render UI for pending HITL requests."""
    adapter = st.session_state.workflow_adapter
    if not adapter:
        return

    pending = adapter.get_pending_requests()

    for request_info in pending:
        # pending requests are now dicts with request_id, data, response_type
        request_id = request_info["request_id"]
        request_data = request_info["data"]

        if isinstance(request_data, SongIdeaRequest):
            render_idea_request(adapter, request_id, request_data)

        elif isinstance(request_data, LyricApprovalRequest):
            render_approval_request(adapter, request_id, request_data)


def render_idea_request(adapter, request_id: str, request: SongIdeaRequest):
    """Render song idea input form."""
    st.markdown("---")
    st.subheader("Template Generated!")

    with st.expander("View Template", expanded=True):
        st.markdown(request.template)

    st.markdown(request.prompt)

    # Create two columns for input and surprise button
    col1, col2 = st.columns([3, 1])

    with col1:
        idea = st.text_input(
            "Song idea or title",
            key="song_idea_input",
            placeholder="e.g., 'Midnight Reflections' or 'Breaking Free'"
        )

    with col2:
        st.write("")  # Spacing
        st.write("")
        surprise_me = st.button("Surprise Me", use_container_width=True)

    # Handle surprise me button
    if surprise_me:
        try:
            random_idea = pick_random_idea()
            adapter.submit_response(request_id, random_idea)
            st.success(f"Random idea selected: {random_idea}")
            # Continue workflow
            adapter.run_workflow_sync("")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to pick random idea: {str(e)}")
            logger.error(f"Error picking random idea: {e}")

    # Generate lyrics button
    if idea and idea.strip():
        if st.button("Generate Lyrics", type="primary", use_container_width=True):
            adapter.submit_response(request_id, idea)
            # Continue workflow
            adapter.run_workflow_sync("")
            st.rerun()


def render_approval_request(adapter, request_id: str, request: LyricApprovalRequest):
    """Render lyric approval form."""
    st.markdown("---")
    st.subheader("Generated Lyrics")
    st.markdown(f"*Completed in {request.iterations_used} iteration(s)*")

    st.markdown(request.lyrics)

    # Show feedback history
    if request.feedback_history:
        with st.expander("View Feedback History"):
            for entry in request.feedback_history:
                st.markdown(f"**Iteration {entry['iteration']}**")
                feedback = entry.get("feedback", {})

                if feedback.get("satisfied"):
                    st.success("✅ Reviewer is satisfied with these lyrics!")
                else:
                    st.warning("⚠️ Reviewer has suggestions for improvement")

                if feedback.get("style_feedback"):
                    st.markdown("**Style Feedback:**")
                    st.markdown(feedback["style_feedback"])

                if feedback.get("plagiarism_concerns"):
                    st.markdown("**Plagiarism/Cliché Check:**")
                    st.markdown(feedback["plagiarism_concerns"])

                if feedback.get("revision_suggestions"):
                    st.markdown("**Revision Suggestions:**")
                    st.markdown(feedback["revision_suggestions"])

    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Accept & Continue", type="primary", use_container_width=True):
            adapter.submit_response(request_id, True)
            # Continue workflow
            adapter.run_workflow_sync("")
            st.rerun()

    with col2:
        if st.button("Regenerate", use_container_width=True):
            adapter.submit_response(request_id, False)
            # Continue workflow (will loop back)
            adapter.run_workflow_sync("")
            st.rerun()


def render_output():
    """Render the final workflow output."""
    adapter = st.session_state.workflow_adapter
    if not adapter:
        return

    # Check for errors
    error = adapter.get_error()
    if error:
        st.error(f"Error: {error}")
        return

    # Check for completion
    status = adapter.get_status()
    if status == "complete":
        output = adapter.get_output()
        if output and isinstance(output, WorkflowOutput):
            render_final_output(output)


def render_final_output(output: WorkflowOutput):
    """Render the final Suno-ready outputs."""
    st.markdown("---")
    st.success("✅ Your Suno outputs are ready!")

    st.subheader("Suno-Ready Outputs")

    # Style Prompt
    st.markdown("**Style Prompt**")
    st.markdown("Copy this into Suno's style/genre input:")
    st.code(output.style_prompt, language="text")
    if st.button("📋 Copy Style Prompt", key="copy_style"):
        st.toast("Style prompt copied to clipboard!")

    st.markdown("---")

    # Formatted Lyrics
    st.markdown("**Formatted Lyric Sheet**")
    st.markdown("Copy this into Suno's lyrics input:")
    st.code(output.lyric_sheet, language="text")
    if st.button("📋 Copy Lyric Sheet", key="copy_lyrics"):
        st.toast("Lyric sheet copied to clipboard!")

    # Show iteration history
    if output.feedback_history:
        with st.expander("View Iteration History"):
            for entry in output.feedback_history:
                st.markdown(f"**Iteration {entry.get('iteration', 'N/A')}**")
                st.markdown("**Lyrics:**")
                st.markdown(entry.get("lyrics", ""))

                st.markdown("---")
                st.markdown("**Feedback:**")
                feedback = entry.get("feedback", {})

                if feedback.get("satisfied"):
                    st.success("✅ Reviewer is satisfied")
                else:
                    st.warning("⚠️ Reviewer suggested improvements")

                if feedback.get("style_feedback"):
                    st.markdown(feedback["style_feedback"])


def run_workflow():
    """Execute the workflow pipeline."""
    adapter = st.session_state.workflow_adapter
    if not adapter:
        st.error("Workflow not initialized")
        return

    # Build initial input
    inputs = st.session_state.workflow_inputs

    # Validate at least one input is provided
    if not any([inputs["artists"].strip(), inputs["songs"].strip(), inputs["guidance"].strip()]):
        st.error("Please provide at least one of: Artist(s), Song(s), or guidance")
        return

    # Build prompt for template agent
    initial_input = f"Artist(s): {inputs['artists']}\nSong(s): {inputs['songs']}\nGuidance: {inputs['guidance']}"

    # Show progress
    with st.spinner("Generating lyric blueprint..."):
        try:
            adapter.run_workflow_sync(initial_input)
            logger.info("Workflow started successfully")
        except Exception as e:
            st.error(f"Workflow execution error: {str(e)}")
            logger.error(f"Workflow execution error: {e}")

    st.rerun()


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

    # Show form or HITL requests based on status
    adapter = st.session_state.workflow_adapter
    if adapter:
        status = adapter.get_status()

        if status == "idle":
            render_workflow_form()
        elif status == "awaiting_input":
            render_hitl_requests()
        elif status == "running":
            st.info("⏳ Workflow is running...")
        elif status == "complete":
            render_output()
        elif status == "error":
            error = adapter.get_error()
            st.error(f"Error: {error}")
            if st.button("Reset Workflow"):
                adapter.reset()
                st.rerun()


if __name__ == "__main__":
    main()
