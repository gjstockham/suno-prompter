<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->


Always use mslearn when I need code generation for Microsoft or Azure setup or configuration steps, or
library/API documentation. This means you should automatically use the mslearn MCP
tools to search for library documentation or code examples without me having to explicitly ask.

Always use context7 when I need code generation for non-Microsoft setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.

## Implementation Verification

Before marking any feature implementation as complete, you MUST verify it works:

```bash
# Create venv (if not exists) and install deps
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Verify the app starts without errors
streamlit run app.py --server.headless true &
sleep 5
pkill -f streamlit
```

If either command fails, fix the errors before declaring implementation complete.