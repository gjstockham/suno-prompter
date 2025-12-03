# Tasks: Refactor Workflow Orchestration to Use Microsoft Agent Framework

## 1. Agent Framework Setup

- [ ] 1.1 Add `agent-framework` and `agent-framework-openai` (or Azure variant) to `requirements.txt`
- [ ] 1.2 Create `agents/factory.py` to centralize chat client creation (supports OpenAI and Azure OpenAI via config)
- [ ] 1.3 Update `agents/__init__.py` to export framework agents instead of custom `LyricTemplateAgent`

## 2. Convert Lyric Template Agent

- [ ] 2.1 Create `agents/lyric_template_agent.py` using `ChatAgent` from Agent Framework
- [ ] 2.2 Define system instructions for lyric template generation
- [ ] 2.3 Wire chat client from factory based on environment config
- [ ] 2.4 Test agent standalone: can call `agent.run()` with test input and get output

## 3. Build Workflow Orchestration

- [ ] 3.1 Refactor `workflows/lyric_workflow.py` to use `WorkflowBuilder`
- [ ] 3.2 Create start executor (lyric-template agent)
- [ ] 3.3 Design workflow build and execution method compatible with Streamlit
- [ ] 3.4 Plan async handling: determine sync wrapper strategy for Streamlit integration

## 4. Streamlit UI Integration

- [ ] 4.1 Update `app.py` to import and initialize Agent Framework workflow
- [ ] 4.2 Modify `run_workflow()` to execute Agent Framework workflow (with async wrapper if needed)
- [ ] 4.3 Handle workflow events (AgentRunUpdateEvent, AgentRunEvent)
- [ ] 4.4 Update progress display to show agent execution status
- [ ] 4.5 Preserve input form values and output display logic
- [ ] 4.6 Test: form submission → workflow execution → blueprint output

## 5. Configuration & Testing

- [ ] 5.1 Validate Agent Framework agent initialization with current config
- [ ] 5.2 Test with OpenAI API (if available) or mock
- [ ] 5.3 Test with Azure OpenAI (if configured)
- [ ] 5.4 Run app locally: `streamlit run app.py --server.headless true`
- [ ] 5.5 Verify complete workflow: input → agent execution → output display

## 6. Cleanup

- [ ] 6.1 Remove old `LyricTemplateAgent` class if not needed by other code
- [ ] 6.2 Update imports across codebase to use new Agent Framework agents
- [ ] 6.3 Remove custom `WorkflowStatus`, `WorkflowInputs`, `WorkflowOutputs` dataclasses if framework replaces them
- [ ] 6.4 Document Agent Framework integration in README or codebase comments

## Dependencies
- Sections 1–2 can run in parallel
- Section 3 depends on completion of Section 2
- Section 4 depends on completion of Section 3
- Sections 5–6 depend on all prior sections

