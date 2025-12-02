"""Lyric workflow orchestration using Microsoft Agent Framework."""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, AsyncIterator

from agent_framework import WorkflowBuilder, AgentRunEvent, AgentRunUpdateEvent, WorkflowStartedEvent, WorkflowStatusEvent, WorkflowFailedEvent
from agents import create_lyric_template_agent
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
    Orchestrator for the lyric generation pipeline using WorkflowBuilder.

    Coordinates sequential execution of agents:
    1. LyricTemplateAgent - Analyzes songs and generates blueprints
    2. (Future) LyricWriterAgent
    3. (Future) LyricReviewerAgent
    4. (Future) SongArrangerAgent
    """

    def __init__(self):
        """Initialize the workflow with required agents."""
        try:
            self.lyric_template_agent = create_lyric_template_agent()
            self.workflow = self._build_workflow()
            logger.info("LyricWorkflow initialized with WorkflowBuilder")
        except Exception as e:
            logger.error(f"Error initializing LyricWorkflow: {e}")
            raise

    def _build_workflow(self):
        """
        Build the workflow using WorkflowBuilder.

        Returns:
            Workflow: Configured workflow instance
        """
        builder = WorkflowBuilder()
        builder.set_start_executor(self.lyric_template_agent)
        # Future: Add edges for additional agents
        # builder.add_edge(self.lyric_template_agent, self.lyric_writer_agent)
        # etc.
        return builder.build()

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

            # Step 1: Run workflow
            logger.info("Running workflow...")
            prompt = f"Please analyze the following and generate a lyric blueprint:\n\n{reference}"

            # Get or create event loop
            loop = self._get_event_loop()

            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(self._run_workflow_async(prompt))
            else:
                result = loop.run_until_complete(self._run_workflow_async(prompt))

            # Extract output from workflow result
            state.outputs.template = result

            state.status = WorkflowStatus.COMPLETE
            logger.info("Workflow completed successfully")

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            state.status = WorkflowStatus.ERROR
            state.error = str(e)

        return state

    async def _run_workflow_async(self, prompt: str) -> str:
        """
        Run the workflow asynchronously.

        Args:
            prompt: The input prompt for the workflow

        Returns:
            str: The generated blueprint markdown
        """
        try:
            output = None

            # Stream events from workflow execution
            async for event in self.workflow.run_stream(prompt):
                if isinstance(event, AgentRunEvent):
                    # Agent has completed execution
                    output = event.data
                    logger.debug(f"Agent {event.executor_id} output received")
                elif isinstance(event, AgentRunUpdateEvent):
                    # Streaming token update (can accumulate if needed)
                    logger.debug(f"Agent {event.executor_id} token: {event.data}")
                elif isinstance(event, WorkflowFailedEvent):
                    raise Exception(f"Workflow failed: {event.details.message}")

            return output or "No blueprint generated"

        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            raise

    def _get_event_loop(self):
        """Get or create an event loop."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

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
