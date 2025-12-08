# Manual Playwright MCP smoke (full end-to-end)

Step-by-step for a tester using Playwright MCP tools (no custom scripts) to exercise the live UI + backend with the song “Vigil in a Wilderness of Mirrors” by Fish. No API mocking.

## Prereqs
- `.env` with valid LLM/provider settings loaded by the backend.
- App running on a safe port: `PORT=7000 python backend/app.py`
- Browser available to Playwright MCP (Chrome installed via `npx playwright install chrome`).
- Network access to your LLM provider (tests will hit real agents).

## Test flow (use these MCP tools)
1) **Open the app**
   - `browser_navigate` to `http://127.0.0.1:7000`
   - Optionally `browser_snapshot` to capture refs for form fields.

2) **Fill the form**
   - Artists: `Fish`
   - Songs: `Vigil in a Wilderness of Mirrors`
   - Song idea / title: `Vigil in a Wilderness of Mirrors`
   - Leave other fields empty; keep producer toggle on.
   - Use `browser_fill_form` (with snapshot refs) or `browser_type` to enter values.

3) **Submit**
   - `browser_click` on “Generate prompt”.

4) **Wait for completion**
   - Use `browser_wait_for` (e.g., wait for text `complete`) or `browser_evaluate` to poll the status pill.
   - Allow generous time (30–60s) for LLM/agent work.

5) **Verify UI**
   - Status pill shows `complete`; no `.callout.error`.
   - Blueprint card shows a non-empty template and the idea.
   - Lyrics card shows generated lyrics text (non-empty).
   - Feedback section shows ≥1 iteration with reviewer status.
   - Suno output section shows style prompt and lyric sheet (producer toggle on).
   - Tools to use: `browser_snapshot` for refs, `browser_evaluate` to assert text presence, `browser_take_screenshot` if needed.

6) **Optional: validation check**
   - Clear references and idea, `browser_click` submit.
   - Expect inline errors: `Add a song idea or title before generating lyrics.` and `Provide at least one reference: artists, songs, lyrics, or guidance.` (depending on what is blank).

## Notes
- This is a full end-to-end run; backend config and provider access must be valid.
- If failures occur, inspect backend logs and provider quotas/keys.***
