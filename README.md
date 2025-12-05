# Suno Prompter

A Streamlit application that leverages the Microsoft Agent Framework to generate creative and detailed music prompts for Suno AI music generation.

## Features

- 🎵 **Template Generation**: AI analyzes reference songs and artists to generate a detailed lyric blueprint
- ✍️ **Lyrics Generation**: Creates original lyrics based on the template and your song idea
- 👁️ **Lyrics Review**: Intelligent reviewer evaluates lyrics for style adherence and plagiarism concerns
- 🔄 **Iterative Refinement**: Refine lyrics through multiple iterations with reviewer feedback (up to 3 revisions)
- 💡 **Smart Ideas**: Choose your own song idea or get a random suggestion from starter ideas
- 🤖 Microsoft Agent Framework (agent-framework) for intelligent assistance
- 🔧 Easy configuration via environment variables - supports OpenAI, Azure OpenAI, and custom OpenAI-compatible endpoints
- ⚡ Async/await patterns for responsive interactions

## Quick Start (uvx - Recommended)

The fastest way to run Suno Prompter without cloning or installing Python:

### 1. Install uv (one-time setup)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configure API credentials

Create a configuration file at `~/.suno-prompter/.env`:

```bash
# Create directory
mkdir -p ~/.suno-prompter

# Create config file (edit with your API key)
cat > ~/.suno-prompter/.env << 'EOF'
# For OpenAI API
OPENAI_API_KEY=your-api-key-here
OPENAI_CHAT_MODEL_ID=gpt-4

# For custom endpoints (Ollama, LM Studio, etc.)
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_CHAT_MODEL_ID=llama3
EOF
```

### 3. Run the app

```bash
uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter
```

The application will automatically:
- Download Python if needed
- Install dependencies
- Launch in your browser

## Requirements

- Python 3.10 or higher (auto-installed by `uv` if needed)
- OpenAI API key, Azure OpenAI credentials, or access to a custom OpenAI-compatible endpoint

## Installation (Traditional)

### 1. Clone the repository

```bash
git clone https://github.com/gjstockham/suno-prompter
cd suno-prompter
```

### 2. Install the package

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

### 3. Configure environment variables

Create a `.env` file in the current directory or at `~/.suno-prompter/.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
# For OpenAI API
OPENAI_API_KEY=your-key-here
OPENAI_CHAT_MODEL_ID=gpt-4

# For custom endpoints (Ollama, LM Studio, etc.)
# OPENAI_BASE_URL=http://localhost:11434/v1
# OPENAI_CHAT_MODEL_ID=llama3
```

### 4. Run the application

```bash
# Using the installed command
suno-prompter

# Or as a module
python -m suno_prompter
```

## Usage

The application will automatically open in your default browser when you run it. If using the traditional installation, you can start it with `suno-prompter` or `python -m suno_prompter`.

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

The application supports any OpenAI-compatible API:

**Required:**
- `OPENAI_CHAT_MODEL_ID` - The model to use (e.g., `gpt-4`, `llama3`)

**For OpenAI API:**
- `OPENAI_API_KEY` - Your OpenAI API key

**For Custom Endpoints (Ollama, LM Studio, etc.):**
- `OPENAI_BASE_URL` - Custom API endpoint URL (e.g., `http://localhost:11434/v1`)
- `OPENAI_API_KEY` - Optional, depends on your endpoint

**Application Settings:**
- `APP_DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)

### Environment File Locations

The application looks for `.env` files in this order:
1. Current working directory (`./.env`)
2. Home directory (`~/.suno-prompter/.env`)
3. Environment variables already set in your shell

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
│   ├── lyric_reviewer_agent.py      # Reviews lyrics for quality
│   └── suno_producer_agent.py       # Formats Suno-ready outputs
├── src/suno_prompter/
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── builder.py               # Workflow construction
│   │   ├── types.py                 # HITL request/response types
│   │   └── executors/               # Custom workflow executors
│   │       ├── idea_collector.py    # HITL for song idea
│   │       ├── lyric_generator.py   # Writer/reviewer loop + HITL
│   │       └── output_formatter.py  # Final output formatting
│   └── adapters/
│       └── streamlit_adapter.py     # Streamlit integration
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
        └── migrate-to-framework-workflows/  # Current implementation
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

### Microsoft Agent Framework Workflows

The application uses Microsoft's Agent Framework with native workflow orchestration:

**Workflow Graph:**
```
template_agent → IdeaCollector → LyricGenerator → producer_agent → OutputFormatter
                 (HITL: idea)    (HITL: approval)
```

**Key Components:**
- **WorkflowBuilder**: Constructs the workflow graph with auto-wrapped agents
- **Custom Executors**: Handle human-in-the-loop (HITL) interactions and complex logic
  - `IdeaCollector`: Requests song idea from user
  - `LyricGenerator`: Runs writer/reviewer loop with approval HITL
  - `OutputFormatter`: Formats final Suno-ready outputs
- **StreamlitWorkflowAdapter**: Bridges framework events with Streamlit's execution model
- **HITL Pattern**: Uses `request_info()` and `@response_handler` for user interactions

**Benefits:**
- ✅ Native framework patterns (no custom orchestration)
- ✅ Event-driven architecture with `run_stream()` and `send_responses_streaming()`
- ✅ Portable workflow logic (can run via CLI, API, or UI)
- ✅ Type-safe HITL requests and responses
- ✅ No async workarounds needed (removed `nest_asyncio`)

### Configuration Management

`config.py` handles all environment variable loading and validation:
- OpenAI API key support
- Azure OpenAI support (endpoint, API key, deployment name)
- Custom OpenAI-compatible endpoints (Ollama, LM Studio, etc.)
- Application settings (debug mode, logging level)

### Streamlit UI

The Streamlit adapter provides:
- Workflow execution via adapter pattern
- HITL request rendering and response submission
- Session state management for workflow persistence
- Real-time event streaming and status updates

## Implementation Status

### Completed
- [x] Template generation from reference songs
- [x] Lyric writer agent
- [x] Lyric reviewer agent with plagiarism/cliché detection
- [x] Iterative refinement loop (up to 3 revisions)
- [x] Human-in-loop idea collection
- [x] Random idea suggestion from starter ideas
- [x] Suno producer agent for formatted outputs
- [x] **Migration to Microsoft Agent Framework Workflows**
  - [x] Native `WorkflowBuilder` orchestration
  - [x] HITL via `request_info()` and `@response_handler`
  - [x] Custom executors for HITL and complex logic
  - [x] Streamlit adapter for event-driven UI
  - [x] Removed `nest_asyncio` dependency

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
- [ ] CLI adapter for terminal-based usage
- [ ] Workflow checkpointing and resume capability

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
