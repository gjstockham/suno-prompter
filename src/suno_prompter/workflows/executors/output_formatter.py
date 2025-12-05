"""
OutputFormatter executor for parsing producer output and yielding final result.
"""
import json
import re
from typing import Dict, Any
from typing_extensions import Never

from agent_framework import (
    Executor,
    WorkflowContext,
    handler,
    AgentExecutorResponse,
)

from ..types import WorkflowOutput


class OutputFormatter(Executor):
    """
    Formats final output from producer agent.

    Input: AgentExecutorResponse from producer_agent + context
    Output: WorkflowOutput (yielded as final result)
    """

    def __init__(self):
        super().__init__(id="output_formatter")
        self._pending_context: Dict[str, Any] = {}

    @handler
    async def on_lyrics_context(
        self, context_data: Dict[str, Any], ctx: WorkflowContext
    ) -> None:
        """Store context data (lyrics and history) for final output."""
        self._pending_context = context_data

    @handler
    async def on_producer_response(
        self,
        response: AgentExecutorResponse,
        ctx: WorkflowContext[Never, WorkflowOutput],
    ) -> None:
        """Parse producer output and yield final result."""
        producer_output = self._parse_producer_output(
            response.agent_run_response.text
        )

        # Get the template from pending context if available
        # Otherwise try to extract from the conversation history
        template = self._pending_context.get("template", "")

        final_output = WorkflowOutput(
            style_prompt=producer_output.get("style_prompt", ""),
            lyric_sheet=producer_output.get("lyric_sheet", ""),
            template=template,
            original_lyrics=self._pending_context.get("lyrics", ""),
            feedback_history=self._pending_context.get("feedback_history", []),
        )

        await ctx.yield_output(final_output)

    def _parse_producer_output(self, output: str) -> Dict[str, str]:
        """Parse JSON output from producer agent."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            json_match = re.search(
                r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", output, re.DOTALL
            )
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Fallback: return raw output
            return {
                "style_prompt": "Error: Could not parse",
                "lyric_sheet": output,
            }
