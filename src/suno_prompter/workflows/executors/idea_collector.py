"""
IdeaCollector executor for requesting song ideas from users.
"""
from agent_framework import (
    Executor,
    WorkflowContext,
    handler,
    response_handler,
    AgentExecutorResponse,
)

from ..types import SongIdeaRequest


class IdeaCollector(Executor):
    """
    Collects song idea from user after template generation.

    Input: AgentExecutorResponse from template_agent
    Output: dict with template and idea
    HITL: Requests song idea via SongIdeaRequest
    """

    def __init__(self):
        super().__init__(id="idea_collector")

    @handler
    async def on_template(
        self, response: AgentExecutorResponse, ctx: WorkflowContext
    ) -> None:
        """Receive template from template_agent, request idea from user."""
        template = response.agent_run_response.text

        # Request song idea from user (HITL)
        await ctx.request_info(
            request_data=SongIdeaRequest(template=template), response_type=str
        )

    @response_handler
    async def on_idea_response(
        self, original_request: SongIdeaRequest, idea: str, ctx: WorkflowContext
    ) -> None:
        """User provided song idea, forward to lyric generation."""
        await ctx.send_message(
            {"template": original_request.template, "idea": idea}
        )
