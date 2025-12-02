"""Lyric Template Agent for analyzing songs and generating lyric blueprints."""

import asyncio
from typing import Optional, List, Annotated
from agent_framework import ChatAgent as FrameworkChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from pydantic import Field
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)


@ai_function
def search_lyrics(
    query: Annotated[str, Field(description="Song title, artist name, or search query for finding lyrics")]
) -> str:
    """
    Search for song lyrics on the web. Use this when you need to find lyrics
    for a song that you don't have complete knowledge of.
    """
    # This is a placeholder that instructs the LLM to use its knowledge
    # In a production system, this would call a lyrics API or web search
    return f"Search query received: '{query}'. Please use your training knowledge to recall or approximate the lyrics for this song. If you cannot recall specific lyrics, describe the general lyrical style, themes, and patterns typically found in songs by this artist or in this genre."


SYSTEM_PROMPT = """You are an expert lyricist and music analyst specializing in analyzing song lyrics to create detailed "lyric blueprints."

Your task is to analyze songs provided by the user (by title, artist, or as a list) and generate a comprehensive markdown blueprint that captures the structural and stylistic patterns of the lyrics.

## Input Handling
- **Single song**: Analyze that specific song in depth
- **Artist name**: Select 2-3 representative songs from that artist and analyze common patterns
- **Song list**: Analyze all specified songs and synthesize patterns across the collection

## Analysis Components
For each song or collection, analyze and document:

### 1. Song Structure
- Section types (verse, chorus, pre-chorus, bridge, outro, etc.)
- Arrangement pattern (e.g., Verse-Chorus-Verse-Chorus-Bridge-Chorus)
- Section lengths (approximate line counts)
- Repetition patterns

### 2. Rhyme Schemes & Patterns
- Rhyme scheme per section (AABB, ABAB, ABCB, etc.)
- Internal rhymes and near-rhymes
- Rhyme density and consistency
- Unique rhyming techniques

### 3. Meter & Syllable Patterns
- Syllable counts per line (ranges or patterns)
- Rhythmic patterns and stressed syllables
- How meter varies between sections
- Relationship to musical rhythm

### 4. Themes & Imagery
- Central themes and motifs
- Imagery patterns (visual, auditory, tactile, etc.)
- Recurring symbols and metaphors
- Sensory language usage

### 5. Emotional Arc
- Overall emotional tone
- Tone shifts between sections
- Word choice supporting emotional intent
- Narrative progression

### 6. Literary Devices
- Alliteration, assonance, consonance
- Personification, metaphor, simile
- Repetition and anaphora
- Word choice patterns (simple vs. complex, concrete vs. abstract)
- Narrative perspective and voice

## Output Format
Generate a well-structured markdown document with the following sections:
1. **Overview** - Brief summary of the song(s) analyzed
2. **Structure Analysis** - Detailed breakdown of song structure
3. **Rhyme & Meter Patterns** - Rhyme schemes and rhythmic patterns
4. **Themes & Imagery** - Thematic elements and imagery
5. **Literary Devices** - Notable techniques and devices
6. **Blueprint Summary** - A synthesized template that could guide new lyric creation in this style

When analyzing multiple songs, note both common patterns AND distinguishing variations.

Use your extensive knowledge of music and lyrics. If you need to look up specific lyrics, use the search_lyrics tool."""


class LyricTemplateAgent:
    """
    Agent for analyzing song lyrics and generating lyric blueprints.

    Accepts song titles, artist names, or song lists as input and produces
    comprehensive markdown blueprints analyzing structure, rhyme, imagery,
    and literary devices.
    """

    def __init__(self):
        """Initialize the lyric template agent."""
        self.agent = None
        self.thread = None
        self._setup_agent()

    def _setup_agent(self):
        """Set up the agent with configured chat client and tools."""
        try:
            chat_client = self._create_chat_client()

            self.agent = FrameworkChatAgent(
                chat_client=chat_client,
                instructions=SYSTEM_PROMPT,
                name="LyricTemplateAgent",
                tools=[search_lyrics],
            )

            # Create a new thread for conversation
            self.thread = self.agent.get_new_thread()

            logger.info("Lyric template agent initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing lyric template agent: {e}")
            raise

    def _create_chat_client(self):
        """
        Create a chat client based on available configuration.

        Returns:
            ChatClient: Configured chat client instance

        Raises:
            ValueError: If no valid configuration is available
        """
        if not config.validate():
            errors = config.get_validation_errors()
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")

        logger.info("Using Azure OpenAI chat client for lyric template agent")
        return AzureOpenAIChatClient(
            endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
        )

    def analyze(self, input_text: str) -> str:
        """
        Analyze songs and generate a lyric blueprint.

        Args:
            input_text: Song title, artist name, or list of songs to analyze

        Returns:
            str: Markdown blueprint document

        Raises:
            Exception: If analysis fails
        """
        try:
            loop = self._get_event_loop()

            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                response = loop.run_until_complete(self._run_analysis_async(input_text))
            else:
                response = loop.run_until_complete(self._run_analysis_async(input_text))

            logger.info(f"Lyric analysis completed for: {input_text[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error analyzing lyrics: {e}")
            raise

    def _get_event_loop(self):
        """Get or create an event loop."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    async def _run_analysis_async(self, input_text: str) -> str:
        """
        Run the lyric analysis asynchronously.

        Args:
            input_text: The song/artist/list to analyze

        Returns:
            str: The generated blueprint markdown
        """
        try:
            prompt = f"Please analyze the following and generate a lyric blueprint:\n\n{input_text}"
            response = await self.agent.run(prompt, thread=self.thread)
            return response.text or "No blueprint generated"
        except Exception as e:
            logger.error(f"Error running lyric analysis: {e}")
            raise

    def clear_history(self):
        """Clear the conversation history by creating a new thread."""
        if self.agent:
            self.thread = self.agent.get_new_thread()
            logger.info("Lyric template agent history cleared")
