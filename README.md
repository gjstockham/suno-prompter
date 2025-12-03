# Suno Prompter

A Streamlit application that leverages the Microsoft Agent Framework to generate creative and detailed music prompts for Suno AI music generation.

## Features

- 🎵 **Template Generation**: AI analyzes reference songs and artists to generate a detailed lyric blueprint
- ✍️ **Lyrics Generation**: Creates original lyrics based on the template and your song idea
- 👁️ **Lyrics Review**: Intelligent reviewer evaluates lyrics for style adherence and plagiarism concerns
- 🔄 **Iterative Refinement**: Refine lyrics through multiple iterations with reviewer feedback (up to 3 revisions)
- 💡 **Smart Ideas**: Choose your own song idea or get a random suggestion from starter ideas
- 🤖 Microsoft Agent Framework (agent-framework) for intelligent assistance
- 🔧 Easy configuration via environment variables (OpenAI or Azure OpenAI)
- ⚡ Async/await patterns for responsive interactions

## Requirements

- Python 3.10 or higher
- OpenAI API key (or Azure OpenAI credentials)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd suno-prompter
```

### 2. Create a virtual environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and add your API credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Or for Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4
```

## Usage

### Start the application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Workflow: Generate a Lyric Blueprint and Create Lyrics

1. **Enter Reference Information**
   - Artist(s): Enter artists whose style you want to emulate
   - Song(s): Enter specific songs to analyze
   - Other guidance: Add any additional style preferences or requirements

2. **Generate Blueprint** - Click "Generate Blueprint" to create a lyric template

3. **Select a Song Idea**
   - Enter your own song idea/title, or
   - Click "Surprise Me" for a random starter idea

4. **Generate Lyrics** - Click "Generate Lyrics" to create original lyrics based on your template and idea

5. **Review and Iterate**
   - View the generated lyrics and reviewer feedback
   - Feedback includes style adherence and plagiarism/cliché checks
   - Click "Accept & Finalize" to accept the lyrics, or
   - Click "Request Revision" to refine (up to 3 iterations)

6. **Final Output** - View your final lyrics with optional revision history

### Clear Workflow

Use the "Clear Workflow" button in the sidebar to start a new session.

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required if not using Azure)
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key (alternative)
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_MODEL_DEPLOYMENT` - Your model deployment name on Azure
- `APP_DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)

## Project Structure

```
suno-prompter/
├── app.py                           # Main Streamlit application
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── README.md                        # This file
├── agents/
│   ├── __init__.py
│   ├── lyric_template_agent.py      # Generates lyric blueprints
│   ├── lyric_writer_agent.py        # Generates lyrics from template + idea
│   └── lyric_reviewer_agent.py      # Reviews lyrics for quality
├── workflows/
│   ├── __init__.py
│   └── lyric_workflow.py            # Orchestrates template → writer → reviewer loop
├── utils/
│   ├── __init__.py
│   ├── logging.py                   # Logging utilities
│   └── ideas.py                     # Starter idea selection
├── data/
│   └── starter_ideas.txt            # 10 song idea prompts
└── openspec/
    ├── project.md                   # Project context and conventions
    └── changes/
        ├── archive/                 # Archived proposals
        └── generate-and-review-lyrics/  # Current proposal
```

## Development

### Local Development with Hot Reload

Streamlit automatically reloads the app when you save changes:

```bash
streamlit run app.py
```

Modify `app.py` or other files and save - the app will update automatically.

### Debugging

Enable debug mode in `.env`:

```
APP_DEBUG=true
LOG_LEVEL=DEBUG
```

Check the terminal output for detailed logs.

## Testing

### Manual Testing

1. Start the application
2. Test basic message submission
3. Test multi-turn conversation
4. Test error handling (submit message without valid API key)
5. Test clearing conversation

### API Key Validation

The application validates API configuration on startup. If configuration is invalid, you'll see a clear error message with instructions.

## Troubleshooting

### "Configuration Error" message

**Solution:** Ensure your `.env` file is properly configured:
- Copy `.env.example` to `.env`
- Add your API key
- Restart the application

### Agent initialization fails

**Solution:** Check your API key and ensure:
- The key is valid and has permissions
- The API endpoint is accessible from your network
- Rate limits haven't been exceeded

### Conversation doesn't load

**Solution:** This is expected behavior in the MVP. Conversation history is stored in Streamlit session state and will be cleared when:
- You refresh the page
- You click "Clear Conversation"
- You restart the application

## Architecture

### Microsoft Agent Framework

The application uses Microsoft's official Agent Framework (`agent-framework`) for AI capabilities:
- **ChatAgent**: The primary agent that handles conversations
- **Chat Clients**: Supports OpenAI and Azure OpenAI backends
- **Thread Management**: Maintains multi-turn conversation context
- **Async Processing**: Built on async/await for responsive interactions

### Configuration Management

`config.py` handles all environment variable loading and validation:
- OpenAI API key support
- Azure OpenAI support (endpoint, API key, deployment name)
- Application settings (debug mode, logging level)

### Streamlit UI

The Streamlit interface provides:
- Chat message display
- User input handling
- Session state management
- Real-time message rendering

## Implementation Status

### Completed
- [x] Template generation from reference songs
- [x] Lyric writer agent
- [x] Lyric reviewer agent with plagiarism/cliché detection
- [x] Iterative refinement loop (up to 3 revisions)
- [x] Human-in-loop idea collection
- [x] Random idea suggestion from starter ideas

### Future Enhancements

- [ ] Export/save generated lyrics to file
- [ ] Session persistence (database storage)
- [ ] Multiple session history
- [ ] Prompt template library
- [ ] Integration with Suno API for direct generation
- [ ] User authentication and multi-user support
- [ ] Advanced analytics on lyrics quality and styles
- [ ] Customizable iteration limits
- [ ] Additional starter ideas source (API/database)

## Contributing

This project uses **OpenSpec** for spec-driven development. Changes are planned, approved, then implemented.

### OpenSpec Quick Guide

OpenSpec follows a three-stage workflow:

| Stage | What Happens | Claude Command |
|-------|--------------|----------------|
| **1. Propose** | Create a change proposal with specs | `/openspec:proposal` |
| **2. Implement** | Build the approved change | `/openspec:apply` |
| **3. Archive** | Archive after deployment | `/openspec:archive` |

### When to Create a Proposal

**Create a proposal for:**
- New features or capabilities
- Breaking changes (API, schema)
- Architecture changes

**Skip proposals for:**
- Bug fixes, typos, comments
- Dependency updates (non-breaking)
- Config changes

### Using the Slash Commands

```
# Start a new proposal (Claude will guide you through it)
/openspec:proposal

# Implement an approved proposal
/openspec:apply

# Archive after deployment
/openspec:archive
```

### Key Directories

```
openspec/
├── specs/      # Current truth (what IS built)
├── changes/    # Proposals (what SHOULD change)
└── project.md  # Project conventions
```

### CLI Commands (Manual)

```bash
openspec list              # List active changes
openspec list --specs      # List specifications
openspec validate --strict # Validate a change
openspec archive <id>      # Archive after deployment
```

For full details, see `openspec/AGENTS.md`.

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in the terminal
3. Check your API key configuration
