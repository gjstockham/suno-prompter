import { useMemo, useState, type ChangeEvent, type FormEvent } from 'react'
import './App.css'
import {
  type FeedbackEntry,
  type PromptRequestPayload,
  type PromptResponse,
  generatePrompt,
} from './services/api'

type FormState = {
  artists: string
  songs: string
  guidance: string
  lyrics: string
  idea: string
  producerGuidance: string
  includeProducer: boolean
}

const emptyForm: FormState = {
  artists: '',
  songs: '',
  guidance: '',
  lyrics: '',
  idea: '',
  producerGuidance: '',
  includeProducer: true,
}

function App() {
  const [form, setForm] = useState<FormState>({ ...emptyForm })
  const [result, setResult] = useState<PromptResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const latestFeedback: FeedbackEntry | undefined = useMemo(
    () => result?.outputs.feedback_history.at(-1),
    [result],
  )

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (!form.idea.trim()) {
      setError('Add a song idea or title before generating lyrics.')
      return
    }

    if (
      ![form.artists, form.songs, form.guidance, form.lyrics].some((value) =>
        value.trim(),
      )
    ) {
      setError('Provide at least one reference: artists, songs, lyrics, or guidance.')
      return
    }

    setIsSubmitting(true)
    try {
      const payload: PromptRequestPayload = {
        artists: form.artists.trim(),
        songs: form.songs.trim(),
        guidance: form.guidance.trim(),
        lyrics: form.lyrics.trim(),
        idea: form.idea.trim(),
        producer_guidance: form.producerGuidance.trim(),
        include_producer: form.includeProducer,
      }

      const response = await generatePrompt(payload)
      setResult(response)
    } catch (err) {
      setResult(null)
      setError(err instanceof Error ? err.message : 'Unable to reach the API right now.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReset = () => {
    setForm({ ...emptyForm })
    setResult(null)
    setError(null)
  }

  const updateField =
    (field: keyof FormState) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm((prev) => ({ ...prev, [field]: event.target.value }))
    }

  return (
    <div className="page">
      <div className="shell">
        <header className="hero">
          <div className="eyebrow">Flask API · React/Vite frontend</div>
          <h1>
            Suno Prompter, rebuilt
            <span className="accent-dot" aria-hidden="true">
              ●
            </span>
          </h1>
          <p className="lede">
            Gather your artist and song references, feed them to the lyric workflow, and get back a
            blueprint, draft lyrics, reviewer notes, and Suno-ready prompts.
          </p>
          <div className="status-row">
            <span className="pill">POST /api/generate-prompt</span>
            <span className={`pill status ${result ? `status-${result.status}` : 'status-idle'}`}>
              {result ? result.status : 'idle'}
            </span>
            {result?.error && <span className="pill warning">Workflow reported an issue</span>}
          </div>
        </header>

        <div className="grid">
          <form className="panel form-panel" onSubmit={handleSubmit}>
            <div className="panel-header">
              <div>
                <p className="label">References</p>
                <h2>Guide the lyric style</h2>
                <p className="muted">
                  Add at least one reference so the template agent has something to analyze.
                </p>
              </div>
              <button className="ghost" type="button" onClick={handleReset}>
                Reset
              </button>
            </div>

            <div className="field-grid">
              <label className="field">
                <span>Artists</span>
                <input
                  type="text"
                  placeholder="e.g., Taylor Swift, Ed Sheeran"
                  value={form.artists}
                  onChange={updateField('artists')}
                />
                <small className="muted">Comma-separated list</small>
              </label>

              <label className="field">
                <span>Songs</span>
                <input
                  type="text"
                  placeholder="e.g., Cruel Summer, Shape of You"
                  value={form.songs}
                  onChange={updateField('songs')}
                />
              </label>
            </div>

            <label className="field">
              <span>Other guidance</span>
              <textarea
                rows={3}
                placeholder="Tone, perspective, tempo, emotional beats..."
                value={form.guidance}
                onChange={updateField('guidance')}
              />
            </label>

            <label className="field">
              <span>Paste lyrics (optional)</span>
              <textarea
                rows={3}
                placeholder="Paste exact lyrics to analyze instead of relying on recall."
                value={form.lyrics}
                onChange={updateField('lyrics')}
              />
            </label>

            <div className="panel-header compact">
              <div>
                <p className="label">Story</p>
                <h3>Song idea</h3>
              </div>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={form.includeProducer}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, includeProducer: event.target.checked }))
                  }
                />
                <span>Also generate Suno style prompt</span>
              </label>
            </div>

            <label className="field">
              <span>Song idea / title</span>
              <input
                type="text"
                placeholder="Midnight skylines over the city"
                value={form.idea}
                onChange={updateField('idea')}
                required
              />
            </label>

            <label className="field">
              <span>Production guidance (for Suno)</span>
              <textarea
                rows={2}
                placeholder="Energy, references, desired sound design..."
                value={form.producerGuidance}
                onChange={updateField('producerGuidance')}
              />
            </label>

            <div className="actions">
              <button className="primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Working…' : 'Generate prompt'}
              </button>
              <span className="muted">
                The backend orchestrates template → writer → reviewer (and producer if enabled).
              </span>
            </div>

            {error && <div className="callout error">{error}</div>}
          </form>

          <div className="panel results-panel">
            <div className="panel-header">
              <div>
                <p className="label">Results</p>
                <h2>Agent output</h2>
                <p className="muted">
                  See the blueprint, lyrics, reviewer notes, and Suno prompts returned by the API.
                </p>
              </div>
            </div>

            {isSubmitting && <div className="callout">The agents are thinking…</div>}
            {result?.error && <div className="callout warning">{result.error}</div>}

            {result ? (
              <div className="stack">
                <section className="result-card">
                  <div className="result-head">
                    <span className="pill subtle">Blueprint</span>
                    <span className="muted small">
                      Idea: <strong>{result.outputs.idea || form.idea}</strong>
                    </span>
                  </div>
                  <pre className="code-block">
                    {result.outputs.template || 'Template pending from the backend.'}
                  </pre>
                </section>

                <section className="result-card">
                  <div className="result-head">
                    <span className="pill subtle">Lyrics</span>
                    <span className={`pill ${latestFeedback?.feedback?.satisfied ? 'success' : ''}`}>
                      {latestFeedback?.feedback?.satisfied ? 'Reviewer satisfied' : 'In review'}
                    </span>
                  </div>
                  <pre className="code-block">
                    {result.outputs.lyrics || 'Waiting for the writer agent to return lyrics.'}
                  </pre>
                </section>

                <section className="result-card">
                  <div className="result-head">
                    <span className="pill subtle">Feedback</span>
                    <span className="muted small">
                      {result.outputs.feedback_history.length} iteration
                      {result.outputs.feedback_history.length === 1 ? '' : 's'}
                    </span>
                  </div>
                  {result.outputs.feedback_history.length === 0 ? (
                    <p className="muted">No reviewer feedback yet.</p>
                  ) : (
                    <div className="feedback-grid">
                      {result.outputs.feedback_history.map((entry) => (
                        <div className="feedback-card" key={entry.iteration}>
                          <div className="feedback-head">
                            <span className="pill subtle">Iteration {entry.iteration}</span>
                            <span
                              className={`pill ${
                                entry.feedback.satisfied ? 'success' : 'warning-soft'
                              }`}
                            >
                              {entry.feedback.satisfied ? 'Approved' : 'Needs work'}
                            </span>
                          </div>
                          <p className="muted">{entry.feedback.style_feedback}</p>
                          {entry.feedback.plagiarism_concerns && (
                            <p className="muted">Plagiarism check: {entry.feedback.plagiarism_concerns}</p>
                          )}
                          {entry.feedback.revision_suggestions && (
                            <p className="muted">Next revision: {entry.feedback.revision_suggestions}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                {form.includeProducer && (
                  <section className="result-card">
                    <div className="result-head">
                      <span className="pill subtle">Suno output</span>
                    </div>
                    {result.outputs.suno_output ? (
                      <div className="suno-grid">
                        <div>
                          <p className="label">Style prompt</p>
                          <pre className="code-block compact">
                            {result.outputs.suno_output.style_prompt ||
                              'Style prompt is missing from the response.'}
                          </pre>
                        </div>
                        <div>
                          <p className="label">Lyric sheet</p>
                          <pre className="code-block compact">
                            {result.outputs.suno_output.lyric_sheet ||
                              'Lyric sheet is missing from the response.'}
                          </pre>
                        </div>
                      </div>
                    ) : (
                      <p className="muted">Enable the producer toggle to request Suno formatting.</p>
                    )}
                  </section>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <p className="muted">Run the workflow to see results here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
