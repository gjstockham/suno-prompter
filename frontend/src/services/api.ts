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

export async function generatePrompt(
  payload: PromptRequestPayload,
): Promise<PromptResponse> {
  const response = await fetch('/api/generate-prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    const details = Array.isArray(data?.details)
      ? data.details.join(' | ')
      : data?.details

    const message = [data?.error, details].filter(Boolean).join(': ')
    throw new Error(message || 'Unable to generate prompt right now.')
  }

  return data as PromptResponse
}
