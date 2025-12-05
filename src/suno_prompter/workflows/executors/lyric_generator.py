"""
LyricGenerator executor for writer/reviewer iteration loop with user approval.
"""
import json
import re
from typing import Dict, Any, List

from agent_framework import (
    Executor,
    WorkflowContext,
    handler,
    response_handler,
    ChatAgent,
)

from ..types import LyricApprovalRequest


class LyricGenerator(Executor):
    """
    Generates lyrics with writer/reviewer loop and user approval.

    Input: dict with template and idea
    Output: dict with lyrics and feedback_history
    HITL: Requests lyric approval via LyricApprovalRequest
    """

    def __init__(
        self,
        writer_agent: ChatAgent,
        reviewer_agent: ChatAgent,
        max_iterations: int = 3,
    ):
        super().__init__(id="lyric_generator")
        self.writer = writer_agent
        self.reviewer = reviewer_agent
        self.max_iterations = max_iterations

    @handler
    async def generate(
        self, input_data: Dict[str, Any], ctx: WorkflowContext
    ) -> None:
        """Run writer/reviewer loop, then request user approval."""
        template = input_data["template"]
        idea = input_data["idea"]

        feedback_history: List[Dict[str, Any]] = []
        lyrics = None

        for iteration in range(self.max_iterations):
            # Build writer prompt
            if iteration == 0:
                writer_prompt = (
                    f"Style Template:\n{template}\n\n"
                    f"Song Idea/Title: {idea}\n\n"
                    f"Generate complete lyrics matching this template."
                )
            else:
                last_feedback = feedback_history[-1]["feedback"]
                writer_prompt = (
                    f"Style Template:\n{template}\n\n"
                    f"Song Idea/Title: {idea}\n\n"
                    f"Revision Feedback:\n{last_feedback['revision_suggestions']}\n\n"
                    f"Generate revised lyrics incorporating the feedback above."
                )

            # Generate lyrics
            writer_response = await self.writer.run(writer_prompt)
            lyrics = writer_response.text

            # Build reviewer prompt
            reviewer_prompt = (
                f"Style Template:\n{template}\n\n"
                f"Generated Lyrics:\n{lyrics}\n\n"
                f"Provide feedback in JSON format."
            )

            # Review lyrics
            reviewer_response = await self.reviewer.run(reviewer_prompt)
            feedback = self._parse_feedback(reviewer_response.text)

            feedback_history.append(
                {"iteration": iteration + 1, "lyrics": lyrics, "feedback": feedback}
            )

            if feedback.get("satisfied", False):
                break

        # Request user approval (HITL)
        await ctx.request_info(
            request_data=LyricApprovalRequest(
                lyrics=lyrics,
                iterations_used=len(feedback_history),
                feedback_history=feedback_history,
            ),
            response_type=bool,
        )

    @response_handler
    async def on_approval_response(
        self,
        original_request: LyricApprovalRequest,
        approved: bool,
        ctx: WorkflowContext,
    ) -> None:
        """User approved or rejected lyrics."""
        # For MVP, forward to producer regardless of approval
        # In future, could add regeneration logic for rejected lyrics
        await ctx.send_message(
            {
                "lyrics": original_request.lyrics,
                "feedback_history": original_request.feedback_history,
                "user_approved": approved,
            }
        )

    def _parse_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """Parse JSON feedback from reviewer."""
        try:
            return json.loads(feedback_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            json_match = re.search(
                r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", feedback_text, re.DOTALL
            )
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Fallback to default feedback structure
            return {
                "satisfied": False,
                "style_feedback": feedback_text,
                "revision_suggestions": "Please try again.",
            }
