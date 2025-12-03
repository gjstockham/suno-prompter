"""Lyric Template Agent for analyzing songs and generating lyric blueprints."""

from typing import Annotated
from agent_framework import ChatAgent as FrameworkChatAgent, ai_function
from pydantic import Field
from agents.factory import create_chat_client
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


def create_lyric_template_agent() -> FrameworkChatAgent:
    """
    Create and return a ChatAgent for lyric template generation.

    Returns:
        ChatAgent: Configured agent instance

    Raises:
        Exception: If agent creation fails
    """
    try:
        chat_client = create_chat_client()

        agent = FrameworkChatAgent(
            chat_client=chat_client,
            instructions=SYSTEM_PROMPT,
            name="LyricTemplateAgent",
            tools=[search_lyrics],
        )

        logger.info("Lyric template agent created successfully")
        return agent

    except Exception as e:
        logger.error(f"Error creating lyric template agent: {e}")
        raise
