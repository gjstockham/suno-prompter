"""Workflow orchestration for the Suno Prompter application."""

from .builder import build_suno_workflow
from .types import SongIdeaRequest, LyricApprovalRequest, WorkflowOutput

__all__ = [
    "build_suno_workflow",
    "SongIdeaRequest",
    "LyricApprovalRequest",
    "WorkflowOutput",
]
