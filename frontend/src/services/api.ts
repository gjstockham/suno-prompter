export type PromptRequestPayload = {
  artists: string
  songs: string
  guidance: string
  lyrics: string
  idea: string
  producer_guidance: string
  include_producer: boolean
}

export type ReviewerFeedback = {
  satisfied?: boolean
  style_feedback?: string
  plagiarism_concerns?: string
  revision_suggestions?: string
}

export type FeedbackEntry = {
  iteration: number
  lyrics: string
  feedback: ReviewerFeedback
}

export type SunoOutput = {
  style_prompt?: string
  lyric_sheet?: string
} | null

export type PromptResponse = {
  status: string
  error?: string | null
  inputs: PromptRequestPayload
  outputs: {
    template?: string | null
    idea?: string | null
    lyrics?: string | null
    feedback_history: FeedbackEntry[]
    suno_output?: SunoOutput
  }
}

export type TemplateRequestPayload = Pick<
  PromptRequestPayload,
  'artists' | 'songs' | 'guidance' | 'lyrics'
>

export type LyricsRequestPayload = Pick<
  PromptRequestPayload,
  'artists' | 'songs' | 'guidance' | 'lyrics' | 'idea'
> & { template: string }

export type ProductionRequestPayload = Pick<
  PromptRequestPayload,
  'artists' | 'songs' | 'guidance' | 'lyrics' | 'idea' | 'producer_guidance'
> & { template: string }

export type ShuffleIdeaResponse = { idea: string }

async function postJson<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    const details = Array.isArray(data?.details) ? data.details.join(' | ') : data?.details
    const message = [data?.error, details].filter(Boolean).join(': ')
    throw new Error(message || 'Unable to complete that step right now.')
  }

  return data as T
}

export function generatePrompt(payload: PromptRequestPayload): Promise<PromptResponse> {
  return postJson<PromptResponse>('/api/generate-prompt', payload)
}

export function requestTemplate(payload: TemplateRequestPayload): Promise<PromptResponse> {
  return postJson<PromptResponse>('/api/generate-template', payload)
}

export function requestLyrics(payload: LyricsRequestPayload): Promise<PromptResponse> {
  return postJson<PromptResponse>('/api/generate-lyrics', payload)
}

export function requestProduction(payload: ProductionRequestPayload): Promise<PromptResponse> {
  return postJson<PromptResponse>('/api/generate-production', payload)
}

export async function shuffleIdea(): Promise<ShuffleIdeaResponse> {
  const response = await fetch('/api/shuffle-idea')
  const data = await response.json()

  if (!response.ok || !data?.idea) {
    const message = data?.error || 'Unable to shuffle an idea right now.'
    throw new Error(message)
  }

  return data as ShuffleIdeaResponse
}
