"""
Workflow builder for the Suno Prompter application.
"""
from typing import Optional
from agent_framework import WorkflowBuilder, ChatAgent, InMemoryCheckpointStorage, CheckpointStorage

from .executors import IdeaCollector, LyricGenerator, OutputFormatter


def build_suno_workflow(
    template_agent: ChatAgent,
    writer_agent: ChatAgent,
    reviewer_agent: ChatAgent,
    producer_agent: ChatAgent,
    max_iterations: int = 3,
    checkpoint_storage: Optional[CheckpointStorage] = None,
):
    """
    Build the Suno Prompter workflow using framework patterns.

    Workflow graph:
        template_agent → IdeaCollector → LyricGenerator → producer_agent → OutputFormatter
                         (HITL: idea)    (HITL: approval)

    Args:
        template_agent: Agent for generating lyric templates
        writer_agent: Agent for writing lyrics
        reviewer_agent: Agent for reviewing lyrics
        producer_agent: Agent for generating Suno outputs
        max_iterations: Maximum writer/reviewer iterations (default: 3)
        checkpoint_storage: Optional checkpoint storage for state persistence.
                           If None, creates an InMemoryCheckpointStorage.

    Returns:
        Configured Workflow instance
    """
    # Use provided storage or create in-memory storage for checkpointing
    storage = checkpoint_storage or InMemoryCheckpointStorage()

    # Create custom executors
    idea_collector = IdeaCollector()
    lyric_generator = LyricGenerator(writer_agent, reviewer_agent, max_iterations)
    output_formatter = OutputFormatter()

    # Build workflow graph with checkpointing enabled
    workflow = (
        WorkflowBuilder()
        # Start: user input → template agent (auto-wrapped)
        .set_start_executor(template_agent)
        # Template agent → idea collector (HITL for song idea)
        .add_edge(template_agent, idea_collector)
        # Idea collector → lyric generator (writer/reviewer loop + HITL)
        .add_edge(idea_collector, lyric_generator)
        # Lyric generator → producer agent (auto-wrapped)
        .add_edge(lyric_generator, producer_agent)
        # Producer agent → output formatter
        .add_edge(producer_agent, output_formatter)
        # Enable checkpointing for state persistence across Streamlit reruns
        .with_checkpointing(storage)
        .build()
    )

    return workflow, storage
