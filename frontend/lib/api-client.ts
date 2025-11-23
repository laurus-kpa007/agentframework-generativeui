/**
 * API client for communicating with FastAPI backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface StreamEvent {
  type: 'text' | 'component' | 'tool_call' | 'error' | 'done'
  content?: string
  component?: string
  props?: any
  tool?: string
  status?: string
  message?: string
}

export class APIClient {
  private baseUrl: string

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/api/health`)
    if (!response.ok) {
      throw new Error('Health check failed')
    }
    return response.json()
  }

  async* streamChat(message: string): AsyncGenerator<StreamEvent> {
    const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('No response body')
    }

    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.substring(6)
          try {
            const event: StreamEvent = JSON.parse(data)
            yield event

            if (event.type === 'done') {
              return
            }
          } catch (e) {
            console.error('Failed to parse SSE event:', e)
          }
        }
      }
    }
  }

  async sendMessage(message: string, conversationId?: string) {
    const response = await fetch(`${this.baseUrl}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }
}

export const apiClient = new APIClient()
