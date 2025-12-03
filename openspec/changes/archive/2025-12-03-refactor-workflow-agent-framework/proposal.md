# Change: Refactor Workflow Orchestration to Use Microsoft Agent Framework

## Why
The current workflow uses a custom orchestration pattern (`LyricWorkflow` class) that manually coordinates agent execution. To align with the project's stated tech stack and leverage production-grade orchestration patterns, we need to adopt the Microsoft Agent Framework's built-in orchestration capabilities. This enables:
- Standardized agent communication and lifecycle management
- Native support for streaming responses and progress tracking
- Future extensibility to concurrent, handoff, and complex patterns
- Better integration with Azure AI services if needed

## What Changes
- Replace custom `LyricWorkflow` orchestration with Microsoft Agent Framework's `WorkflowBuilder` and sequential orchestration
- Refactor agents to inherit from Agent Framework's `ChatAgent` base class (instead of custom `LyricTemplateAgent`)
- Update Streamlit UI to integrate with Agent Framework's async/await model and streaming events
- Remove custom orchestration state management; use Agent Framework's built-in thread and conversation history
- Restructure agent definitions to use standard Agent Framework patterns (chat client + instructions)

## Impact
- Affected specs: `workflow-orchestration` (MODIFIED), `streamlit-app` (MODIFIED)
- Affected code:
  - `workflows/lyric_workflow.py` - Refactored to use Agent Framework WorkflowBuilder
  - `agents/lyric_template_agent.py` - Converted to ChatAgent-based implementation
  - `app.py` - Updated to support async execution and streaming events
- **BREAKING**: Application initialization and agent execution patterns change; custom `LyricWorkflow.run()` API removed in favor of Agent Framework's workflow execution model

