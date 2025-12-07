"""Lyric workflow orchestration using Microsoft Agent Framework."""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple

from agent_framework import AgentRunEvent, AgentRunUpdateEvent, WorkflowFailedEvent
from ..agents import create_lyric_template_agent, create_lyric_writer_agent, create_lyric_reviewer_agent, create_suno_producer_agent
from ..agents.lyric_reviewer_agent import ReviewerFeedback
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Constants
MAX_ITERATIONS = 3


class WorkflowStatus(Enum):
    """Status of the workflow execution."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class FeedbackEntry:
    """Single feedback iteration entry."""
    iteration: int
    lyrics: str
    feedback: dict  # Contains: satisfied, style_feedback, plagiarism_concerns, revision_suggestions


@dataclass
class WorkflowInputs:
    """Input data for the lyric workflow."""

    artists: str = ""
    songs: str = ""
    guidance: str = ""
    idea: str = ""  # Song idea or title
    lyrics: str = ""  # Optional pasted reference lyrics
    producer_guidance: str = ""  # Production style guidance for Suno output


@dataclass
class WorkflowOutputs:
    """Output data from each agent in the workflow pipeline."""

    template: Optional[str] = None
    idea: Optional[str] = None
    lyrics: Optional[str] = None
    feedback_history: List[FeedbackEntry] = field(default_factory=list)
    suno_output: Optional[dict] = None  # Contains: style_prompt, lyric_sheet


@dataclass
class WorkflowState:
    """Complete state of a workflow execution."""

    inputs: WorkflowInputs = field(default_factory=WorkflowInputs)
    outputs: WorkflowOutputs = field(default_factory=WorkflowOutputs)
    status: WorkflowStatus = WorkflowStatus.IDLE
    error: Optional[str] = None


class LyricWorkflow:
    """
    Orchestrator for the lyric generation pipeline using Agent Framework.

    Coordinates sequential execution of agents:
    1. LyricTemplateAgent - Analyzes songs and generates blueprints
    2. LyricWriterAgent - Generates lyrics from template + idea
    3. LyricReviewerAgent - Critiques lyrics and provides feedback (with iteration loop)
    """

    def __init__(self):
        """Initialize the workflow with required agents."""
        try:
            self.lyric_template_agent = create_lyric_template_agent()
            self.lyric_writer_agent = create_lyric_writer_agent()
            self.lyric_reviewer_agent = create_lyric_reviewer_agent()
            self.suno_producer_agent = create_suno_producer_agent()
            logger.info("LyricWorkflow initialized with all agents")
        except Exception as e:
            logger.error(f"Error initializing LyricWorkflow: {e}")
            raise

    def run(self, inputs: WorkflowInputs) -> WorkflowState:
        """
        Run the full pipeline with the given inputs.

        Args:
            inputs: WorkflowInputs containing artists, songs, guidance, and idea

        Returns:
            WorkflowState containing all outputs and final status
        """
        state = WorkflowState(inputs=inputs, status=WorkflowStatus.RUNNING)

        try:
            # Step 1: Generate template from reference
            logger.info("Step 1: Generating style template...")
            reference = self._build_reference(inputs)

            if not reference.strip():
                state.status = WorkflowStatus.ERROR
                state.error = "Please provide at least one of: Artist(s), Song(s), or guidance"
                return state

            prompt = f"Please analyze the following and generate a lyric blueprint:\n\n{reference}"
            loop = self._get_event_loop()

            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                template = loop.run_until_complete(self._run_agent_async(self.lyric_template_agent, prompt))
            else:
                template = loop.run_until_complete(self._run_agent_async(self.lyric_template_agent, prompt))

            state.outputs.template = template
            state.outputs.idea = inputs.idea

            # Step 2: Generate lyrics with writer agent (iterating with reviewer)
            logger.info("Step 2: Generating and reviewing lyrics...")
            forbidden_phrases = self._build_forbidden_phrases(inputs)
            logger.debug(f"Forbidden phrases ({len(forbidden_phrases)}): {forbidden_phrases}")
            lyrics, feedback_history = loop.run_until_complete(
                self._generate_and_review_lyrics(template, inputs.idea, forbidden_phrases)
            )

            state.outputs.lyrics = lyrics
            state.outputs.feedback_history = feedback_history

            state.status = WorkflowStatus.COMPLETE
            logger.info("Workflow completed successfully")

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            state.status = WorkflowStatus.ERROR
            state.error = str(e)

        return state

    async def _generate_and_review_lyrics(self, template: str, idea: str, forbidden_phrases: Optional[List[str]] = None) -> tuple:
        """
        Generate lyrics and iterate with reviewer until satisfied or max iterations.

        Args:
            template: The style template
            idea: The song idea/title
            forbidden_phrases: Titles/phrases from the references that must not appear in new lyrics

        Returns:
            tuple: (final_lyrics, feedback_history)
        """
        feedback_history = []
        current_lyrics = None
        satisfied = False
        iteration = 0

        while iteration < MAX_ITERATIONS and not satisfied:
            iteration += 1
            logger.info(f"Iteration {iteration}/{MAX_ITERATIONS}")

        # Generate lyrics
            if iteration == 1:
                # First iteration: just idea
                writer_prompt = (
                    "Style Template (analysis only; do NOT reuse exact titles/phrases):\n"
                    f"{template}\n\n"
                    f"Song Idea/Title: {idea}\n"
                    f"Forbidden titles/phrases to avoid entirely (do not paraphrase): {', '.join(forbidden_phrases) if forbidden_phrases else 'None explicitly provided; still avoid lifting hooks or album titles from the template.'}\n\n"
                    "Generate complete lyrics matching this template with fresh wording."
                )
            else:
                # Subsequent iterations: include feedback
                if not feedback_history:
                    logger.warning("No prior feedback available for revision; reverting to first-pass prompt.")
                    last_feedback = {"revision_suggestions": "Rewrite with fresh imagery; avoid any repeated hooks/titles."}
                else:
                    last_feedback = feedback_history[-1]["feedback"]
                writer_prompt = (
                    "Style Template (analysis only; do NOT reuse exact titles/phrases):\n"
                    f"{template}\n\n"
                    f"Song Idea/Title: {idea}\n"
                    f"Forbidden titles/phrases to avoid entirely (do not paraphrase): {', '.join(forbidden_phrases) if forbidden_phrases else 'None explicitly provided; still avoid lifting hooks or album titles from the template.'}\n\n"
                f"Revision Feedback:\n{last_feedback['revision_suggestions']}\n\n"
                "Generate revised lyrics incorporating the feedback above without reusing any reference hooks."
            )

            logger.debug(f"Writer prompt (len={len(writer_prompt)}): {writer_prompt[:600]}")
            current_lyrics = await self._run_agent_async(self.lyric_writer_agent, writer_prompt)
            logger.info(f"Generated lyrics ({len(current_lyrics)} chars)")

            # Review lyrics
            reviewer_prompt = (
                f"Style Template:\n{template}\n\n"
                f"Generated Lyrics:\n{current_lyrics}\n\n"
                f"Forbidden titles/phrases that must NOT appear (if present, set satisfied=false and flag plagiarism): {', '.join(forbidden_phrases) if forbidden_phrases else 'Reference song/album titles and hooks implied by the template.'}\n\n"
                "Provide feedback in JSON format."
            )
            logger.debug(f"Reviewer prompt (len={len(reviewer_prompt)}): {reviewer_prompt[:600]}")
            feedback_json = await self._run_agent_async(self.lyric_reviewer_agent, reviewer_prompt)

            # Parse feedback
            try:
                # Try to extract JSON from response
                feedback_dict = self._parse_reviewer_feedback(feedback_json)
            except Exception as e:
                logger.warning(f"Failed to parse feedback JSON: {e}. Using default feedback.")
                feedback_dict = {
                    "satisfied": False,
                    "style_feedback": feedback_json,
                    "plagiarism_concerns": "",
                    "revision_suggestions": "Please try again.",
                }

            feedback_history.append({
                "iteration": iteration,
                "lyrics": current_lyrics,
                "feedback": feedback_dict
            })

            satisfied = feedback_dict.get("satisfied", False)
            logger.info(f"Reviewer satisfied: {satisfied}")

        return current_lyrics, [FeedbackEntry(**entry) for entry in feedback_history]

    async def _run_agent_async(self, agent, prompt: str) -> str:
        """
        Run an agent asynchronously and accumulate its output.

        Args:
            agent: The agent to run
            prompt: The input prompt

        Returns:
            str: The accumulated output
        """
        output = None
        accumulated_text = []

        try:
            # Create a new thread for this agent run
            thread = agent.get_new_thread()
            response = await agent.run(prompt, thread=thread)

            if response:
                output = response.text if hasattr(response, 'text') else str(response)

            logger.debug(f"Agent output: {len(output) if output else 0} chars")
            return output or "No output generated"

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            raise

    def _parse_reviewer_feedback(self, feedback_json: str) -> dict:
        """
        Parse JSON feedback from reviewer.

        Args:
            feedback_json: Raw JSON string from reviewer

        Returns:
            dict: Parsed feedback with keys: satisfied, style_feedback, plagiarism_concerns, revision_suggestions

        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        # Try to extract JSON from the response (might have extra text)
        try:
            # First try direct parse
            return json.loads(feedback_json)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', feedback_json, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
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
        if inputs.lyrics.strip():
            parts.append("Provided Lyrics (authoritative reference for analysis only; do NOT reuse exact phrases):")
            parts.append(inputs.lyrics.strip())
        return "\n".join(parts)

    def _build_forbidden_phrases(self, inputs: WorkflowInputs) -> List[str]:
        """Collect reference titles/phrases that should never appear in generated lyrics."""
        phrases: List[str] = []
        if inputs.songs.strip():
            phrases.extend([s.strip() for s in inputs.songs.split(",") if s.strip()])
        if inputs.artists.strip():
            phrases.extend([a.strip() for a in inputs.artists.split(",") if a.strip()])
        # Explicit lyrics reference should not be quoted verbatim
        if inputs.lyrics.strip():
            phrases.append("Any direct lines or titles from the provided lyrics")
            phrases.extend(self._extract_forbidden_phrases_from_lyrics(inputs.lyrics))
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for p in phrases:
            key = p.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(p)
        return deduped

    def _extract_forbidden_phrases_from_lyrics(self, lyrics: str, max_phrases: int = 15) -> List[str]:
        """
        Heuristically extract recurring n-grams from provided lyrics to treat as forbidden hooks.

        We look for 3-6 word n-grams that appear at least twice and return the top ones.
        """
        import re
        from collections import Counter

        # Normalize and tokenize
        tokens = re.findall(r"[a-zA-Z']+", lyrics.lower())
        if not tokens:
            return []

        ngram_counts: Counter[Tuple[str, ...]] = Counter()
        for n in range(3, 7):  # 3-6 grams
            for i in range(len(tokens) - n + 1):
                ngram = tuple(tokens[i : i + n])
                ngram_counts[ngram] += 1

        # Keep n-grams that repeat
        repeated = [(ng, c) for ng, c in ngram_counts.items() if c >= 2]
        repeated.sort(key=lambda x: (-x[1], -len(x[0])))  # frequency desc, then length desc

        phrases: List[str] = []
        for ng, count in repeated:
            phrase = " ".join(ng)
            if phrase not in phrases:
                phrases.append(phrase)
            if len(phrases) >= max_phrases:
                break

        return phrases

    def run_producer(self, state: WorkflowState) -> WorkflowState:
        """
        Run the producer agent to generate Suno-compatible outputs.

        Args:
            state: Current workflow state with finalized lyrics

        Returns:
            Updated WorkflowState with suno_output populated
        """
        if state.status != WorkflowStatus.COMPLETE:
            state.error = "Cannot run producer: lyrics must be finalized first"
            logger.error(state.error)
            return state

        if not state.outputs.lyrics:
            state.error = "Cannot run producer: no lyrics available"
            logger.error(state.error)
            return state

        try:
            logger.info("Running producer agent to generate Suno outputs...")

            # Build prompt for producer
            prompt_parts = [
                "Finalized Lyrics:",
                state.outputs.lyrics,
                "",
                "Style Template:",
                state.outputs.template or "No template provided",
            ]

            if state.inputs.producer_guidance.strip():
                prompt_parts.extend([
                    "",
                    "Production Guidance:",
                    state.inputs.producer_guidance.strip()
                ])

            prompt = "\n".join(prompt_parts)

            # Run producer agent
            loop = self._get_event_loop()

            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                producer_output = loop.run_until_complete(
                    self._run_agent_async(self.suno_producer_agent, prompt)
                )
            else:
                producer_output = loop.run_until_complete(
                    self._run_agent_async(self.suno_producer_agent, prompt)
                )

            # Parse JSON output
            suno_output = self._parse_producer_output(producer_output)
            state.outputs.suno_output = suno_output

            logger.info("Producer agent completed successfully")

        except Exception as e:
            logger.error(f"Producer error: {e}")
            state.error = f"Producer error: {str(e)}"

        return state

    def _parse_producer_output(self, output: str) -> dict:
        """
        Parse JSON output from producer agent.

        Args:
            output: Raw output string from producer agent

        Returns:
            dict: Parsed output with style_prompt and lyric_sheet

        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        try:
            # First try direct parse
            return json.loads(output)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            # If still can't parse, return error structure
            logger.warning(f"Failed to parse producer output as JSON: {output[:200]}")
            return {
                "style_prompt": "Error: Could not parse style prompt",
                "lyric_sheet": output
            }
