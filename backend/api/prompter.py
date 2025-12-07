"""API routes for prompt generation."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.services import config
from backend.services.utils.logging import get_logger
from backend.services.workflows import (
    FeedbackEntry,
    LyricWorkflow,
    WorkflowInputs,
    WorkflowState,
    WorkflowStatus,
)

api_bp = Blueprint("prompter_api", __name__, url_prefix="/api")
logger = get_logger(__name__)

_workflow: LyricWorkflow | None = None


def _get_workflow() -> LyricWorkflow:
    """Lazily initialize a workflow instance so we avoid construction on import."""
    global _workflow
    if _workflow is None:
        _workflow = LyricWorkflow()
    return _workflow


def _serialize_feedback(entry: FeedbackEntry) -> dict:
    """Convert FeedbackEntry dataclass into JSON-friendly dict."""
    return {
        "iteration": entry.iteration,
        "lyrics": entry.lyrics,
        "feedback": entry.feedback,
    }


def _serialize_state(state: WorkflowState) -> dict:
    """Convert WorkflowState to a JSON-friendly representation."""
    return {
        "status": state.status.value,
        "error": state.error,
        "inputs": {
            "artists": state.inputs.artists,
            "songs": state.inputs.songs,
            "guidance": state.inputs.guidance,
            "lyrics": state.inputs.lyrics,
            "idea": state.inputs.idea,
            "producer_guidance": state.inputs.producer_guidance,
        },
        "outputs": {
            "template": state.outputs.template,
            "idea": state.outputs.idea,
            "lyrics": state.outputs.lyrics,
            "feedback_history": [
                _serialize_feedback(entry) for entry in state.outputs.feedback_history
            ],
            "suno_output": state.outputs.suno_output,
        },
    }


@api_bp.route("/generate-prompt", methods=["POST"])
def generate_prompt():
    """
    Run the lyric workflow and return results as JSON.

    Expected JSON payload:
    {
        "artists": str,
        "songs": str,
        "lyrics": str,
        "guidance": str,
        "idea": str,
        "producer_guidance": str,
        "include_producer": bool  # optional, run producer agent when true
    }
    """
    payload = request.get_json(silent=True) or {}

    config_errors = config.get_validation_errors()
    if config_errors:
        return (
            jsonify(
                {
                    "error": "Invalid configuration",
                    "details": config_errors,
                }
            ),
            400,
        )

    # Validate required user input
    artists = payload.get("artists", "") or ""
    songs = payload.get("songs", "") or ""
    guidance = payload.get("guidance", "") or ""
    lyrics = payload.get("lyrics", "") or ""
    idea = payload.get("idea", "") or ""
    producer_guidance = payload.get("producer_guidance", "") or ""
    include_producer = bool(payload.get("include_producer"))

    if not any([artists.strip(), songs.strip(), guidance.strip(), lyrics.strip()]):
        return (
            jsonify(
                {
                    "error": "Missing required inputs",
                    "details": "Provide at least one of artists, songs, lyrics, or guidance.",
                }
            ),
            400,
        )

    if not idea.strip():
        return (
            jsonify(
                {
                    "error": "Missing idea/title",
                    "details": "Provide a song idea or title to generate lyrics.",
                }
            ),
            400,
        )

    try:
        inputs = WorkflowInputs(
            artists=artists,
            songs=songs,
            guidance=guidance,
            lyrics=lyrics,
            idea=idea,
            producer_guidance=producer_guidance,
        )
        workflow = _get_workflow()
        state = workflow.run(inputs)

        if include_producer and state.status == WorkflowStatus.COMPLETE:
            state = workflow.run_producer(state)

        response = _serialize_state(state)
        status_code = 200 if state.status != WorkflowStatus.ERROR and not state.error else 400
        return jsonify(response), status_code

    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to generate prompt")
        return jsonify({"error": "Internal server error", "details": str(exc)}), 500
