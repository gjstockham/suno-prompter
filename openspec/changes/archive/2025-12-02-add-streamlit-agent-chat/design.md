# Design: Streamlit App with Microsoft Agent Framework Chat

## Context
The project needs a user-facing interface for interacting with AI agents that generate and refine music prompts for Suno. This is the foundational layer upon which all future features build. Key stakeholders: developers and end users who will use the prompter.

## Goals
- Establish a minimal, working Streamlit application
- Integrate Microsoft Agent Framework for AI capabilities
- Enable multi-turn conversations with state persistence
- Provide clear separation of concerns (UI, config, agents)
- Support future expansion with prompt generation and refinement features

**Non-Goals:**
- Advanced UI customization (stick to Streamlit defaults)
- Multi-user session management
- Persistence to database (in-memory for MVP)
- Production deployment (local development focus)

## Decisions

### Decision 1: Use Streamlit for UI
**What:** Streamlit as the primary UI framework
**Why:**
- Rapid development iteration with hot reload
- Minimal boilerplate for data apps
- Built-in state management
- Excellent for AI/ML applications
- Matches project's local-first development model

**Alternatives considered:**
- FastAPI + React: More complex, overkill for MVP
- Flask: Requires separate frontend build
- Gradio: Good for ML but less flexible than Streamlit

### Decision 2: Microsoft Agent Framework (autogen)
**What:** Use Microsoft autogen (or similar Agent Framework) for agent orchestration
**Why:**
- Native support for multi-step reasoning
- Built-in tool use and function calling
- Handles prompt refinement workflows naturally
- Integrates well with Azure OpenAI services
- Designed for agentic workflows

**Alternatives considered:**
- LangChain: Good but more middleware than framework
- Direct API calls: Lacks structure for complex workflows
- Custom agent implementation: Too much boilerplate

### Decision 3: Configuration via Environment Variables
**What:** Use `.env` files and environment variables for API keys and settings
**Why:**
- Standard Python practice
- No credentials in code
- Easy local development with `.env`
- CI/CD compatible
- Respects project privacy constraints

**Alternatives considered:**
- Hardcoded config: Security risk
- Secrets management service: Overkill for MVP
- Interactive prompts: User friction

### Decision 4: Session State in Memory
**What:** Use Streamlit's session state for conversation history (no persistence)
**Why:**
- Aligned with MVP scope
- Matches local development focus
- No database setup needed
- Users can copy/save conversations manually if needed
- Can add persistence later as needed

**Alternatives considered:**
- SQLite database: Adds complexity, not needed yet
- Redis: Requires external service
- JSON file storage: Simple but clunky for multiple users

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Streamlit hot reload in production | Low | Document that this is for development; address in future deployment spec |
| API costs spiral with agent calls | Medium | Add rate limiting and token counting; monitor in development |
| Agent framework learning curve | Medium | Provide example agents; document patterns in architecture |
| Session state lost on app refresh | Expected | Inform users; consider saving feature later if needed |

## Migration Plan
This is an MVP establishment, not a migration. Rollback: delete the `app.py` and related files if needed.

## Technical Approach

### Project Structure
```
suno-prompter/
├── app.py                 # Main Streamlit app
├── config.py              # Configuration and env vars
├── requirements.txt       # Dependencies
├── .env.example           # Template for local setup
├── agents/
│   ├── __init__.py
│   └── chat_agent.py      # Basic chat agent using Agent Framework
└── utils/
    ├── __init__.py
    └── logging.py         # Simple logging utilities
```

### Minimal Dependencies
```
streamlit==1.28+
pyautogen>=0.2.0  # Microsoft Agent Framework
python-dotenv>=1.0.0
```

### Application Flow
1. User starts `streamlit run app.py`
2. Load configuration from `.env`
3. Initialize chat agent on first run
4. Display chat interface with Streamlit components
5. Handle user messages → Agent processing → Display response
6. Maintain conversation history in session state

### Error Handling
- Validate API keys on startup
- Display user-friendly errors for API failures
- Log errors for debugging
- Graceful degradation if external services unavailable

## Open Questions
- Which specific Agent Framework should we use? (autogen vs others)
- Do we need chat history export/save feature in MVP?
- Should we implement prompt caching for cost optimization?
- How do we handle long-running agent operations?
