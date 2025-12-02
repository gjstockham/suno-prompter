"""Lyric workflow orchestration for sequential agent execution."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agents import LyricTemplateAgent
from utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowStatus(Enum):
    """Status of the workflow execution."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class WorkflowInputs:
    """Input data for the lyric workflow."""

    artists: str = ""
    songs: str = ""
    guidance: str = ""


@dataclass
class WorkflowOutputs:
    """Output data from each agent in the workflow pipeline."""

    template: Optional[str] = None
    # Future agents' outputs
    lyrics: Optional[str] = None
    reviewed: Optional[str] = None
    arranged: Optional[str] = None


@dataclass
class WorkflowState:
    """Complete state of a workflow execution."""

    inputs: WorkflowInputs = field(default_factory=WorkflowInputs)
    outputs: WorkflowOutputs = field(default_factory=WorkflowOutputs)
    status: WorkflowStatus = WorkflowStatus.IDLE
    error: Optional[str] = None


class LyricWorkflow:
    """
    Orchestrator for the lyric generation pipeline.

    Coordinates sequential execution of agents:
    1. LyricTemplateAgent - Analyzes songs and generates blueprints
    2. (Future) LyricWriterAgent
    3. (Future) LyricReviewerAgent
    4. (Future) SongArrangerAgent
    """

    def __init__(self):
        """Initialize the workflow with required agents."""
        self.agents = {
            "template": LyricTemplateAgent(),
            # Future agents added here
        }
        logger.info("LyricWorkflow initialized")

    def run(self, inputs: WorkflowInputs) -> WorkflowState:
        """
        Run the full pipeline with the given inputs.

        Args:
            inputs: WorkflowInputs containing artists, songs, and guidance

        Returns:
            WorkflowState containing all outputs and final status
        """
        state = WorkflowState(inputs=inputs, status=WorkflowStatus.RUNNING)

        try:
            # Build the reference string from inputs
            reference = self._build_reference(inputs)

            if not reference.strip():
                state.status = WorkflowStatus.ERROR
                state.error = "Please provide at least one of: Artist(s), Song(s), or guidance"
                return state

            # Step 1: Run template agent
            logger.info("Running template agent...")
            state.outputs.template = self.agents["template"].analyze(reference)

            # Future steps would chain here:
            # state.outputs.lyrics = self.agents["writer"].write(state.outputs.template)
            # state.outputs.reviewed = self.agents["reviewer"].review(state.outputs.lyrics)
            # state.outputs.arranged = self.agents["arranger"].arrange(state.outputs.reviewed)

            state.status = WorkflowStatus.COMPLETE
            logger.info("Workflow completed successfully")

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            state.status = WorkflowStatus.ERROR
            state.error = str(e)

        return state

    def _build_reference(self, inputs: WorkflowInputs) -> str:
        """
        Combine artist, songs, and guidance into a reference string.

        Args:
            inputs: WorkflowInputs containing the user's specifications

        Returns:
            Formatted reference string for the agents
        """
        parts = []
        if inputs.artists.strip():
            parts.append(f"Artist(s): {inputs.artists.strip()}")
        if inputs.songs.strip():
            parts.append(f"Song(s): {inputs.songs.strip()}")
        if inputs.guidance.strip():
            parts.append(f"Additional guidance: {inputs.guidance.strip()}")
        return "\n".join(parts)
