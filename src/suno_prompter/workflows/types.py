"""
Type definitions for workflow human-in-the-loop requests and outputs.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class SongIdeaRequest:
    """Request song idea from user after template generation."""

    template: str
    prompt: str = "Please provide a song idea or title:"


@dataclass
class LyricApprovalRequest:
    """Request user approval of generated lyrics."""

    lyrics: str
    iterations_used: int
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    prompt: str = "Review the generated lyrics:"


@dataclass
class WorkflowOutput:
    """Final workflow output with Suno-ready data."""

    style_prompt: str
    lyric_sheet: str
    template: str
    original_lyrics: str
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
