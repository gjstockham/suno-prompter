"""
Streamlit adapter for the Microsoft Agent Framework workflow.

Uses checkpointing to persist workflow state across Streamlit reruns.
"""
import streamlit as st
import asyncio
from typing import Optional, List, Dict, Any

from agent_framework import (
    RequestInfoEvent,
    WorkflowOutputEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
    CheckpointStorage,
)


def _get_or_create_event_loop():
    """Get the current event loop or create a new one."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


class StreamlitWorkflowAdapter:
    """
    Adapts framework workflow to Streamlit's execution model using checkpointing.

    Key design:
    - Workflow state is persisted via CheckpointStorage (survives reruns)
    - Pending HITL requests are stored in session state
    - On resume, workflow re-emits RequestInfoEvent from checkpoint
    - Responses are sent via send_responses_streaming()

    Flow:
    1. run_workflow(input) - starts workflow, collects events until HITL or complete
    2. submit_response(request_id, response) - stores response in session state
    3. continue_workflow() - resumes from checkpoint, sends responses
    """

    def __init__(self, workflow, checkpoint_storage: CheckpointStorage):
        """
        Initialize the adapter with a workflow and checkpoint storage.

        Args:
            workflow: A workflow instance built with WorkflowBuilder (with checkpointing).
            checkpoint_storage: The checkpoint storage used by the workflow.
        """
        self.workflow = workflow
        self.checkpoint_storage = checkpoint_storage
        self._loop = _get_or_create_event_loop()
        self._init_session_state()

    def _init_session_state(self):
        """Initialize Streamlit session state."""
        if "wf_state" not in st.session_state:
            st.session_state.wf_state = {
                "status": "idle",
                "checkpoint_id": None,  # Current checkpoint for resuming
                "pending_requests": [],  # List of RequestInfoEvent data
                "responses": {},  # Dict of request_id -> response
                "output": None,
                "error": None,
            }

    def run_workflow_sync(self, initial_input: str):
        """
        Synchronous wrapper to run or continue the workflow.

        If there are pending responses, sends them via send_responses_streaming().
        Otherwise starts a new run or resumes from checkpoint.
        """
        self._loop.run_until_complete(self._run_workflow_async(initial_input))

    async def _run_workflow_async(self, initial_input: str):
        """
        Run workflow and collect events until HITL request or completion.

        This method handles three scenarios:
        1. Fresh start: no checkpoint, run with initial_input
        2. Resume with responses: checkpoint exists, send responses
        3. Resume without responses: checkpoint exists, re-emit pending requests
        """
        state = st.session_state.wf_state
        state["status"] = "running"
        state["pending_requests"] = []

        try:
            # Determine which stream to use
            if state["responses"]:
                # We have responses to send - use send_responses_streaming
                stream = self.workflow.send_responses_streaming(state["responses"])
                state["responses"] = {}  # Clear after sending
            elif state["checkpoint_id"]:
                # Resume from checkpoint (re-emits pending requests)
                stream = self.workflow.run_stream(checkpoint_id=state["checkpoint_id"])
            else:
                # Fresh start
                stream = self.workflow.run_stream(initial_input)

            # Collect events
            await self._collect_events(stream, state)

        except Exception as e:
            state["error"] = str(e)
            state["status"] = "error"
            import traceback
            traceback.print_exc()

    async def _collect_events(self, stream, state: Dict[str, Any]):
        """Collect events from stream and update state accordingly."""
        async for event in stream:
            print(f"[Adapter] Event: {type(event).__name__}")  # Debug logging

            if isinstance(event, RequestInfoEvent):
                # Store the request for UI rendering
                state["pending_requests"].append({
                    "request_id": event.request_id,
                    "data": event.data,
                    "response_type": event.response_type,
                })
                state["status"] = "awaiting_input"

            elif isinstance(event, WorkflowOutputEvent):
                print(f"[Adapter] Output received: {event.data}")  # Debug
                state["output"] = event.data
                state["status"] = "complete"
                state["checkpoint_id"] = None  # Clear checkpoint on completion

            elif isinstance(event, WorkflowStatusEvent):
                print(f"[Adapter] Status: {event.state}")  # Debug
                # Track workflow state for checkpoint management
                if event.state == WorkflowRunState.IDLE_WITH_PENDING_REQUESTS:
                    state["status"] = "awaiting_input"
                    # Get latest checkpoint ID for resumption
                    await self._update_checkpoint_id(state)
                elif event.state == WorkflowRunState.IDLE:
                    # Workflow completed without pending requests
                    # If we have no output and no pending requests, keep as running
                    # The output should come via WorkflowOutputEvent
                    if state["status"] == "running" and not state["pending_requests"]:
                        # Workflow is idle but we didn't get an output event yet
                        # This could mean the workflow completed without yielding output
                        print(f"[Adapter] Workflow IDLE, no output yet")
                        pass  # Will be set to complete when we get WorkflowOutputEvent

    async def _update_checkpoint_id(self, state: Dict[str, Any]):
        """Get the latest checkpoint ID from storage."""
        try:
            checkpoints = await self.checkpoint_storage.list_checkpoints()
            if checkpoints:
                # Sort by timestamp (most recent first) and get latest
                sorted_checkpoints = sorted(
                    checkpoints, key=lambda cp: cp.timestamp, reverse=True
                )
                state["checkpoint_id"] = sorted_checkpoints[0].checkpoint_id
        except Exception as e:
            print(f"Warning: Could not get checkpoint ID: {e}")

    def submit_response(self, request_id: str, response: Any):
        """Submit user response for a HITL request."""
        state = st.session_state.wf_state
        state["responses"][request_id] = response

        # Remove from pending
        state["pending_requests"] = [
            r for r in state["pending_requests"] if r["request_id"] != request_id
        ]

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get list of pending HITL requests."""
        return st.session_state.wf_state.get("pending_requests", [])

    def get_output(self) -> Optional[Any]:
        """Get workflow output if complete."""
        return st.session_state.wf_state.get("output")

    def get_status(self) -> str:
        """Get current workflow status."""
        return st.session_state.wf_state.get("status", "idle")

    def get_error(self) -> Optional[str]:
        """Get error message if any."""
        return st.session_state.wf_state.get("error")

    def reset(self):
        """Reset workflow state."""
        st.session_state.wf_state = {
            "status": "idle",
            "checkpoint_id": None,
            "pending_requests": [],
            "responses": {},
            "output": None,
            "error": None,
        }
