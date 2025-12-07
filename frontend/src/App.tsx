import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from 'react'
import './App.css'
import {
  type FeedbackEntry,
  type PromptRequestPayload,
  type PromptResponse,
  type SunoOutput,
  requestLyrics,
  requestProduction,
  requestTemplate,
} from './services/api'

type Stage = 'references' | 'lyricsFallback' | 'idea' | 'producer' | 'complete'

const emptyInputs: PromptRequestPayload = {
  artists: '',
  songs: '',
  guidance: '',
  lyrics: '',
  idea: '',
  producer_guidance: '',
  include_producer: true,
}

const emptyOutputs = {
  template: null as string | null,
  idea: null as string | null,
  lyrics: null as string | null,
  feedback_history: [] as FeedbackEntry[],
  suno_output: null as SunoOutput,
}

function App() {
  const [stage, setStage] = useState<Stage>('references')
  const [references, setReferences] = useState({ artists: '', songs: '', guidance: '' })
  const [lyricsReference, setLyricsReference] = useState('')
  const [idea, setIdea] = useState('')
  const [producerGuidance, setProducerGuidance] = useState('')
  const [includeProducer, setIncludeProducer] = useState(true)
  const [workflow, setWorkflow] = useState<PromptResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [statusHint, setStatusHint] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const active = document.querySelector('.step-card.active')
    if (active) {
      active.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [stage])

  const latestFeedback: FeedbackEntry | undefined = useMemo(
    () => workflow?.outputs.feedback_history.at(-1),
    [workflow],
  )

  const mergeWorkflow = (next: PromptResponse) => {
    setWorkflow((prev) => {
      const prevInputs = prev?.inputs ?? emptyInputs
      const prevOutputs = prev?.outputs ?? emptyOutputs
      return {
        status: next.status,
        error: next.error,
        inputs: { ...prevInputs, ...next.inputs, include_producer: prevInputs.include_producer },
        outputs: {
          template: next.outputs.template ?? prevOutputs.template,
          idea: next.outputs.idea ?? prevOutputs.idea,
          lyrics: next.outputs.lyrics ?? prevOutputs.lyrics,
          feedback_history:
            next.outputs.feedback_history?.length > 0
              ? next.outputs.feedback_history
              : prevOutputs.feedback_history,
          suno_output: next.outputs.suno_output ?? prevOutputs.suno_output,
        },
      }
    })
  }

  const reset = () => {
    setStage('references')
    setReferences({ artists: '', songs: '', guidance: '' })
    setLyricsReference('')
    setIdea('')
    setProducerGuidance('')
    setIncludeProducer(true)
    setWorkflow(null)
    setError(null)
    setStatusHint(null)
  }

  const handleReferencesSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setStatusHint(null)

    if (![references.artists, references.songs].some((value) => value.trim())) {
      setError('Add at least one artist or song so we can search for a template.')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await requestTemplate({
        artists: references.artists.trim(),
        songs: references.songs.trim(),
        guidance: references.guidance.trim(),
        lyrics: '',
      })

      mergeWorkflow(response)

      if (response.status === 'needs_lyrics') {
        setStage('lyricsFallback')
        setStatusHint(response.error ?? 'No luck finding that combo. Paste lyrics to keep going.')
      } else {
        setStage('idea')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to build a template right now.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleLyricsFallbackSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (!lyricsReference.trim()) {
      setError('Paste a chunk of lyrics so we can analyze the style.')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await requestTemplate({
        artists: references.artists.trim(),
        songs: references.songs.trim(),
        guidance: references.guidance.trim(),
        lyrics: lyricsReference.trim(),
      })
      mergeWorkflow(response)
      if (response.status === 'needs_lyrics') {
        setStatusHint(response.error ?? 'We still need more lyrics to continue.')
      } else {
        setStage('idea')
        setStatusHint(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to build a template from lyrics.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleIdeaSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (!workflow?.outputs.template) {
      setError('Generate a template first.')
      return
    }

    if (!idea.trim()) {
      setError('Add a song idea or title before generating lyrics.')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await requestLyrics({
        artists: references.artists.trim(),
        songs: references.songs.trim(),
        guidance: references.guidance.trim(),
        lyrics: lyricsReference.trim(),
        idea: idea.trim(),
        template: workflow.outputs.template,
      })
      mergeWorkflow(response)
      setStage('producer')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate lyrics right now.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleProducerSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (!workflow?.outputs.lyrics) {
      setError('Generate lyrics first.')
      return
    }

    if (!includeProducer) {
      setWorkflow((prev) =>
        prev
          ? {
              ...prev,
              status: 'complete',
              inputs: { ...prev.inputs, include_producer: false, producer_guidance: producerGuidance },
            }
          : prev,
      )
      setStage('complete')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await requestProduction({
        artists: references.artists.trim(),
        songs: references.songs.trim(),
        guidance: references.guidance.trim(),
        lyrics: workflow.outputs.lyrics || '',
        idea: idea.trim(),
        producer_guidance: producerGuidance.trim(),
        template: workflow.outputs.template || '',
      })
      mergeWorkflow(response)
      setStage('complete')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to generate production guidance.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateReferenceField =
    (field: keyof typeof references) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setReferences((prev) => ({ ...prev, [field]: event.target.value }))
    }

  return (
    <div className="page">
      <div className="shell">
        <header className="hero">
          <div className="eyebrow">Flask API · React/Vite frontend</div>
          <h1>
            Suno Prompter, staged
            <span className="accent-dot" aria-hidden="true">
              ●
            </span>
          </h1>
          <p className="lede">
            Move through the flow one checkpoint at a time: lock a style template, pitch your idea,
            draft lyrics, then finish with production guidance for Suno.
          </p>
          <div className="status-row">
            <span className="pill">POST /api/generate-*</span>
            <span className={`pill status status-${workflow?.status || stage}`}>
              {workflow?.status || stage}
            </span>
            {workflow?.error && <span className="pill warning">Workflow reported an issue</span>}
            <button className="ghost" type="button" onClick={reset}>
              Start over
            </button>
          </div>
        </header>

        <div className="grid">
          <div className="stack">
            <section
              className={`panel step-card ${stage === 'references' ? 'active' : 'done'} ${
                stage !== 'references' ? 'collapsed' : ''
              }`}
            >
              <div className="panel-header">
                <div>
                  <p className="label">Step 1 · References</p>
                  <h2>Search by artist + song</h2>
                  <p className="muted">We&apos;ll try to build a style template from this combo first.</p>
                </div>
              </div>

              <form className="step-form" onSubmit={handleReferencesSubmit}>
                <div className="field-grid">
                  <label className="field">
                    <span>Artists</span>
                    <input
                      type="text"
                      placeholder="e.g., Taylor Swift"
                      value={references.artists}
                      onChange={updateReferenceField('artists')}
                    />
                  </label>
                  <label className="field">
                    <span>Songs</span>
                    <input
                      type="text"
                      placeholder="e.g., Cruel Summer"
                      value={references.songs}
                      onChange={updateReferenceField('songs')}
                    />
                  </label>
                </div>

                <label className="field">
                  <span>Other guidance (optional)</span>
                  <textarea
                    rows={2}
                    placeholder="Tempo, mood, perspective..."
                    value={references.guidance}
                    onChange={updateReferenceField('guidance')}
                  />
                </label>

                <div className="actions">
                  <button className="primary" type="submit" disabled={isSubmitting}>
                    {isSubmitting && stage === 'references' ? 'Searching…' : 'Build template'}
                  </button>
                  <span className="muted">If we can&apos;t match this combo, we&apos;ll ask for lyrics next.</span>
                </div>
              </form>

              {stage !== 'references' && (
                <div className="summary">
                  <span className="pill subtle">Locked in</span>{' '}
                  {[references.artists, references.songs].filter(Boolean).join(' · ') ||
                    'No references entered'}
                </div>
              )}
            </section>

            {stage === 'lyricsFallback' && (
              <section className="panel step-card active">
                <div className="panel-header">
                  <div>
                    <p className="label">Step 2 · Paste lyrics</p>
                    <h3>We need the source lyrics</h3>
                    <p className="muted">Drop in a verse or chorus so we can analyze the style.</p>
                  </div>
                </div>

                <form className="step-form" onSubmit={handleLyricsFallbackSubmit}>
                  <label className="field">
                    <span>Lyrics to analyze</span>
                    <textarea
                      rows={4}
                      placeholder="Paste the exact lyrics from that artist + song combo."
                      value={lyricsReference}
                      onChange={(event) => setLyricsReference(event.target.value)}
                    />
                  </label>

                  <div className="actions">
                    <button className="primary" type="submit" disabled={isSubmitting}>
                      {isSubmitting ? 'Analyzing…' : 'Try again with lyrics'}
                    </button>
                    <span className="muted">
                      {statusHint || 'We only ask for this when search comes up empty.'}
                    </span>
                  </div>
                </form>
              </section>
            )}

            {workflow?.outputs.template && (
              <section
                className={`panel step-card ${stage === 'idea' ? 'active' : 'done'} ${
                  stage !== 'idea' ? 'collapsed' : ''
                }`}
              >
                <div className="panel-header">
                  <div>
                    <p className="label">Step 3 · Story</p>
                    <h3>Lock the idea/title</h3>
                    <p className="muted">We have a template. Now pitch the story you want written.</p>
                  </div>
                </div>

                <form className="step-form" onSubmit={handleIdeaSubmit}>
                  <label className="field">
                    <span>Song idea / title</span>
                    <input
                      type="text"
                      placeholder="Midnight skylines over the city"
                      value={idea}
                      onChange={(event) => setIdea(event.target.value)}
                    />
                  </label>

                  <div className="actions">
                    <button className="primary" type="submit" disabled={isSubmitting}>
                      {isSubmitting && stage === 'idea' ? 'Writing…' : 'Generate lyrics'}
                    </button>
                    <span className="muted">We&apos;ll loop writer + reviewer until the lyrics stick.</span>
                  </div>
                </form>

                {stage !== 'idea' && idea.trim() && (
                  <div className="summary">
                    <span className="pill subtle">Idea</span> {idea}
                  </div>
                )}
              </section>
            )}

            {workflow?.outputs.lyrics && (
              <section
                className={`panel step-card ${stage === 'producer' ? 'active' : 'done'} ${
                  stage !== 'producer' ? 'collapsed' : ''
                }`}
              >
                <div className="panel-header">
                  <div>
                    <p className="label">Step 4 · Production</p>
                    <h3>Guide the Suno output</h3>
                    <p className="muted">
                      Optional, but helps format a stronger style prompt and lyric sheet.
                    </p>
                  </div>
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={includeProducer}
                      onChange={(event) => setIncludeProducer(event.target.checked)}
                    />
                    <span>Generate Suno style prompt</span>
                  </label>
                </div>

                <form className="step-form" onSubmit={handleProducerSubmit}>
                  <label className="field">
                    <span>Production guidance</span>
                    <textarea
                      rows={3}
                      placeholder="Energy, mix notes, comparisons..."
                      value={producerGuidance}
                      onChange={(event) => setProducerGuidance(event.target.value)}
                    />
                  </label>

                  <div className="actions">
                    <button className="primary" type="submit" disabled={isSubmitting}>
                      {isSubmitting && includeProducer
                        ? 'Producing…'
                        : includeProducer
                          ? 'Generate production'
                          : 'Finish without producer'}
                    </button>
                    <span className="muted">You can skip this if you only need the lyrics.</span>
                  </div>
                </form>

                {stage !== 'producer' && (
                  <div className="summary">
                    <span className="pill subtle">Producer</span>{' '}
                    {includeProducer ? 'Enabled' : 'Skipped'}
                    {producerGuidance ? ` · ${producerGuidance}` : ''}
                  </div>
                )}
              </section>
            )}

            {error && <div className="callout error">{error}</div>}
          </div>

          <div className="panel results-panel">
            <div className="panel-header">
              <div>
                <p className="label">Results</p>
                <h2>Agent output</h2>
                <p className="muted">Blueprint → lyrics → feedback iterations → Suno prompts.</p>
              </div>
            </div>

            {isSubmitting && <div className="callout">The agents are thinking…</div>}
            {workflow?.error && <div className="callout warning">{workflow.error}</div>}

            {workflow?.outputs.template ? (
              <div className="stack">
                <section className="result-card">
                  <div className="result-head">
                    <span className="pill subtle">Blueprint</span>
                    <span className="muted small">
                      Idea: <strong>{workflow.outputs.idea || idea || 'TBD'}</strong>
                    </span>
                  </div>
                  <pre className="code-block">
                    {workflow.outputs.template || 'Template pending from the backend.'}
                  </pre>
                </section>

                {workflow.outputs.lyrics && (
                  <section className="result-card">
                    <div className="result-head">
                      <span className="pill subtle">Lyrics</span>
                      <span className={`pill ${latestFeedback?.feedback?.satisfied ? 'success' : ''}`}>
                        {latestFeedback?.feedback?.satisfied ? 'Reviewer satisfied' : 'In review'}
                      </span>
                    </div>
                    <pre className="code-block">
                      {workflow.outputs.lyrics || 'Waiting for the writer agent to return lyrics.'}
                    </pre>
                  </section>
                )}

                {workflow.outputs.feedback_history.length > 0 && (
                  <section className="result-card">
                    <div className="result-head">
                      <span className="pill subtle">Feedback</span>
                      <span className="muted small">
                        {workflow.outputs.feedback_history.length} iteration
                        {workflow.outputs.feedback_history.length === 1 ? '' : 's'}
                      </span>
                    </div>
                    <div className="feedback-grid">
                      {workflow.outputs.feedback_history.map((entry) => (
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
                          <pre className="code-block compact">
                            {entry.lyrics || 'Lyrics not captured for this pass.'}
                          </pre>
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
                  </section>
                )}

                {includeProducer && (
                  <section className="result-card">
                    <div className="result-head">
                      <span className="pill subtle">Suno output</span>
                    </div>
                    {workflow.outputs.suno_output ? (
                      <div className="suno-grid">
                        <div>
                          <p className="label">Style prompt</p>
                          <pre className="code-block compact">
                            {workflow.outputs.suno_output?.style_prompt ||
                              'Style prompt is missing from the response.'}
                          </pre>
                        </div>
                        <div>
                          <p className="label">Lyric sheet</p>
                          <pre className="code-block compact">
                            {workflow.outputs.suno_output?.lyric_sheet ||
                              'Lyric sheet is missing from the response.'}
                          </pre>
                        </div>
                      </div>
                    ) : (
                      <p className="muted">Add production guidance and generate to see the Suno prompt.</p>
                    )}
                  </section>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <p className="muted">Work through the steps to see results here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
