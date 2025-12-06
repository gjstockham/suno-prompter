"""Main Streamlit application for the Suno Prompter."""

import json
import streamlit as st
import streamlit.components.v1 as components
from .config import config
from .utils.logging import get_logger
from .utils.ideas import pick_random_idea
from .workflows import LyricWorkflow
from .workflows.lyric_workflow import WorkflowInputs, WorkflowStatus

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
                "idea": "",
                "producer_guidance": "",
            },
            "outputs": {
                "template": None,
                "idea": None,
                "lyrics": None,
                "feedback_history": [],
                "suno_output": None,
            },
            "status": "idle",
            "error": None,
            "iteration": 0,
            "max_iterations": 3,
        }
    if "workflow_instance" not in st.session_state:
        st.session_state.workflow_instance = None


def render_copy_button(label: str, text: str, key: str):
    """Render a client-side copy-to-clipboard button with inline feedback."""
    if not text:
        st.write("_Nothing to copy yet._")
        return

    safe_text = json.dumps(text)
    components.html(
        f"""
        <div style="margin: 0.5rem 0;">
            <button style="padding: 0.4rem 0.8rem; border-radius: 0.4rem; border: 1px solid #e0e0e0; cursor: pointer; background: #f7f7f7;" onclick="navigator.clipboard.writeText({safe_text}); const el = document.getElementById('{key}-copied'); if (el) {{ el.style.display='inline'; el.innerText='Copied!'; setTimeout(()=>{{el.style.display='none';}}, 1800); }}">{label}</button>
            <span id="{key}-copied" style="display:none; margin-left: 0.5rem; color: #10a37f; font-weight: 600;">Copied!</span>
        </div>
        """,
        height=42,
    )


def validate_configuration():
    """Validate that the application configuration is correct."""
    if not config.validate():
        st.error("Configuration Error")
        errors = config.get_validation_errors()
        error_message = f"""
The application requires LLM configuration.

**Configuration errors:**
{chr(10).join(f'- {err}' for err in errors)}

**Setup instructions:**
1. Create a `.env` file in the current directory or at `~/.suno-prompter/.env`
2. Add your LLM configuration (see .env.example)
3. Restart the application

**Default provider (one of: openai, azure):**
```
LLM_PROVIDER=openai
```

**For OpenAI API:**
```
OPENAI_API_KEY=your-key-here
OPENAI_CHAT_MODEL_ID=gpt-4o
```

**For custom endpoints (Ollama, LM Studio, etc.):**
```
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_CHAT_MODEL_ID=llama3
```

**For Azure OpenAI (deployment-based):**
```
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
```

**Per-agent overrides (optional):**
- TEMPLATE_LLM_PROVIDER=azure
- TEMPLATE_AZURE_DEPLOYMENT_NAME=another-deployment
- WRITER_CHAT_MODEL_ID=gpt-4o-mini
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
                    "idea": "",
                    "producer_guidance": "",
                },
                "outputs": {
                    "template": None,
                    "idea": None,
                    "lyrics": None,
                    "feedback_history": [],
                    "suno_output": None,
                },
                "status": "idle",
                "error": None,
                "iteration": 0,
                "max_iterations": 3,
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


def render_idea_collection():
    """Render the song idea collection UI after template generation."""
    template = st.session_state.workflow["outputs"]["template"]

    if not template:
        return

    st.markdown("---")
    st.subheader("Select a Song Idea")
    st.markdown(
        "Now let's create lyrics based on this template. Do you have a song idea or title in mind?"
    )

    # Create two columns for user input and surprise button
    col1, col2 = st.columns([3, 1])

    with col1:
        idea = st.text_input(
            "Song idea or title",
            value=st.session_state.workflow["inputs"]["idea"],
            placeholder="e.g., 'Midnight Reflections' or 'Breaking Free'",
        )
        st.session_state.workflow["inputs"]["idea"] = idea

    with col2:
        st.write("")
        st.write("")
        surprise_me = st.button("Surprise Me", use_container_width=True)

    if surprise_me:
        try:
            random_idea = pick_random_idea()
            st.session_state.workflow["inputs"]["idea"] = random_idea
            st.success(f"Random idea selected: {random_idea}")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to pick random idea: {str(e)}")
            logger.error(f"Error picking random idea: {e}")

    # Generate lyrics button (only show if idea is provided)
    if st.session_state.workflow["inputs"]["idea"].strip():
        if st.button("Generate Lyrics", type="primary", use_container_width=True):
            st.session_state.workflow["status"] = "generating_lyrics"
            run_workflow_with_idea()


def render_lyrics_and_feedback():
    """Render generated lyrics with reviewer feedback."""
    feedback_history = st.session_state.workflow["outputs"]["feedback_history"]

    if not feedback_history:
        return

    st.markdown("---")
    st.subheader("Generated Lyrics & Feedback")

    # Show current iteration
    current_feedback = feedback_history[-1]
    st.markdown(f"**Iteration {current_feedback.iteration} of {st.session_state.workflow['max_iterations']}**")

    # Show all iterations with lyrics and feedback
    with st.expander("Iteration History", expanded=False):
        for i, entry in enumerate(feedback_history, 1):
            with st.expander(f"Iteration {i}"):
                st.markdown("**Lyrics:**")
                st.markdown(entry.lyrics)

                st.markdown("---")
                st.markdown("**Feedback:**")
                feedback = entry.feedback

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
        if st.button("Accept & Finalize", use_container_width=True, type="primary"):
            st.session_state.workflow["status"] = "complete"
            st.rerun()

    with col2:
        # Only show revise button if not at max iterations
        if current_feedback.iteration < st.session_state.workflow["max_iterations"]:
            if st.button("Request Revision", use_container_width=True):
                st.session_state.workflow["status"] = "generating_lyrics"
                run_workflow_with_idea()
        else:
            st.button("Max Iterations Reached", use_container_width=True, disabled=True)


def render_final_lyrics():
    """Render the final accepted lyrics with revision history."""
    lyrics = st.session_state.workflow["outputs"]["lyrics"]
    feedback_history = st.session_state.workflow["outputs"]["feedback_history"]

    if not lyrics or st.session_state.workflow["status"] != "complete":
        return

    st.markdown("---")
    st.subheader("Final Lyrics")
    st.markdown(lyrics)

    # Show all iterations with lyrics and feedback
    with st.expander("Iteration History", expanded=False):
        for i, entry in enumerate(feedback_history, 1):
            with st.expander(f"Iteration {i}"):
                st.markdown("**Lyrics:**")
                st.markdown(entry.lyrics)

                st.markdown("---")
                st.markdown("**Feedback:**")
                feedback = entry.feedback

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

    st.success("✅ Your lyrics are ready!")

    # Producer section
    render_producer_section()


def render_producer_section():
    """Render the Suno producer section for style prompt and lyric formatting."""
    st.markdown("---")
    st.subheader("Create Suno Output")
    st.markdown(
        "Generate Suno-compatible outputs: a style prompt and formatted lyric sheet with meta-tags."
    )

    # Production guidance input
    producer_guidance = st.text_area(
        "Production Guidance (Optional)",
        value=st.session_state.workflow["inputs"]["producer_guidance"],
        placeholder="Describe the sound you want, reference songs/artists... (e.g., 'upbeat like Taylor Swift's Shake It Off')",
        help="Provide guidance for the production style. You can reference specific songs or artists.",
        height=100,
    )
    st.session_state.workflow["inputs"]["producer_guidance"] = producer_guidance

    # Generate Suno Output button
    if st.button("Generate Suno Output", type="primary", use_container_width=True):
        run_producer()

    # Display Suno output if available
    render_suno_output()


def render_suno_output():
    """Render the generated Suno outputs (style prompt and formatted lyrics)."""
    suno_output = st.session_state.workflow["outputs"]["suno_output"]

    if not suno_output:
        return

    st.markdown("---")
    st.subheader("Suno-Ready Outputs")

    # Style Prompt
    st.markdown("**Style Prompt**")
    st.markdown("Copy this into Suno's style/genre input:")
    style_prompt = suno_output.get("style_prompt", "")
    st.code(style_prompt, language="text")
    render_copy_button("📋 Copy Style Prompt", style_prompt, key="copy_style")

    st.markdown("---")

    # Formatted Lyrics
    st.markdown("**Formatted Lyric Sheet**")
    st.markdown("Copy this into Suno's lyrics input:")
    lyric_sheet = suno_output.get("lyric_sheet", "")
    st.code(lyric_sheet, language="text")
    render_copy_button("📋 Copy Lyric Sheet", lyric_sheet, key="copy_lyrics")

    st.success("✅ Your Suno outputs are ready! Copy them to Suno to generate your song.")


def run_producer():
    """Execute the producer agent to generate Suno outputs."""
    from .workflows.lyric_workflow import WorkflowState, WorkflowOutputs

    # Build current state from session
    current_state = WorkflowState()
    current_state.status = WorkflowStatus.COMPLETE if st.session_state.workflow["status"] == "complete" else WorkflowStatus.IDLE
    current_state.inputs.artists = st.session_state.workflow["inputs"]["artists"]
    current_state.inputs.songs = st.session_state.workflow["inputs"]["songs"]
    current_state.inputs.guidance = st.session_state.workflow["inputs"]["guidance"]
    current_state.inputs.idea = st.session_state.workflow["inputs"]["idea"]
    current_state.inputs.producer_guidance = st.session_state.workflow["inputs"]["producer_guidance"]
    current_state.outputs.template = st.session_state.workflow["outputs"]["template"]
    current_state.outputs.lyrics = st.session_state.workflow["outputs"]["lyrics"]
    current_state.outputs.feedback_history = st.session_state.workflow["outputs"]["feedback_history"]

    # Show progress
    with st.spinner("Generating Suno outputs..."):
        try:
            result = st.session_state.workflow_instance.run_producer(current_state)

            # Update session state with results
            st.session_state.workflow["outputs"]["suno_output"] = result.outputs.suno_output
            if result.error:
                st.error(f"Producer error: {result.error}")
                logger.error(f"Producer failed: {result.error}")
            else:
                logger.info("Producer completed successfully")

        except Exception as e:
            st.error(f"Producer execution error: {str(e)}")
            logger.error(f"Producer execution error: {e}")

    st.rerun()


def run_workflow():
    """Execute the workflow pipeline for template generation."""
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


def run_workflow_with_idea():
    """Execute the workflow pipeline with lyrics generation and review."""
    inputs = WorkflowInputs(
        artists=st.session_state.workflow["inputs"]["artists"],
        songs=st.session_state.workflow["inputs"]["songs"],
        guidance=st.session_state.workflow["inputs"]["guidance"],
        idea=st.session_state.workflow["inputs"]["idea"],
    )

    # Show progress
    with st.spinner("Generating and reviewing lyrics..."):
        try:
            result = st.session_state.workflow_instance.run(inputs)

            # Update session state with results
            st.session_state.workflow["status"] = result.status.value
            st.session_state.workflow["outputs"]["idea"] = result.outputs.idea
            st.session_state.workflow["outputs"]["lyrics"] = result.outputs.lyrics
            st.session_state.workflow["outputs"]["feedback_history"] = result.outputs.feedback_history
            st.session_state.workflow["error"] = result.error

            if result.status == WorkflowStatus.ERROR:
                logger.error(f"Workflow failed: {result.error}")
            else:
                logger.info("Lyrics generation and review completed successfully")

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
    elif status in ["complete", "generating_lyrics", "reviewing"] and template:
        st.markdown("---")

        # Show idea collection if template exists but no feedback history yet
        if not st.session_state.workflow["outputs"]["feedback_history"]:
            st.subheader("Lyric Blueprint")
            st.markdown(template)
            render_idea_collection()
        else:
            # Collapse template section when we have feedback
            with st.expander("Lyric Blueprint", expanded=False):
                st.markdown(template)

            # Show appropriate view based on status
            if status == "complete":
                render_final_lyrics()
            else:
                render_lyrics_and_feedback()


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
