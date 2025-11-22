'use client'

import { useState, useEffect, useRef } from 'react'
import { Send } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { apiClient, StreamEvent } from '@/lib/api-client'
import {
  StockCard,
  WeatherCard,
  FlightCard,
  RecipeCard,
  MovieCard,
  ProductCard,
  HotelCard,
  RestaurantCard,
  BookCard,
  NewsCard,
  EventCard,
  ExerciseCard,
} from '@/components/ui'
import { ModelSelector } from '@/components/chat/model-selector'
import { MCPSettings } from '@/components/mcp/mcp-settings'
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
  components?: Array<{
    name: string
    props: any
  }>
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isStreaming) return

    const userMessage = input.trim()
    setInput('')
    setIsStreaming(true)

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])

    // Create placeholder for assistant message
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
    }

    setMessages((prev) => [...prev, assistantMessage])

    try {
      let fullContent = ''

      for await (const event of apiClient.streamChat(userMessage)) {
        if (event.type === 'text') {
          fullContent += event.content
          assistantMessage.content += event.content
          setMessages((prev) => [
            ...prev.slice(0, -1),
            { ...assistantMessage },
          ])
        } else if (event.type === 'component') {
          // Initialize components array if not exists
          if (!assistantMessage.components) {
            assistantMessage.components = []
          }

          // Add component to array
          assistantMessage.components.push({
            name: event.component!,
            props: event.props,
          })

          // Remove JSON blocks from text content
          const jsonPattern = /```json\s*\{[^`]+?\}\s*```/g
          assistantMessage.content = fullContent.replace(jsonPattern, '').trim()

          setMessages((prev) => [
            ...prev.slice(0, -1),
            { ...assistantMessage },
          ])
        } else if (event.type === 'error') {
          console.error('스트림 에러:', event.message)
        }
      }
    } catch (error) {
      console.error('채팅 스트림 실패:', error)
      assistantMessage.content =
        '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.'
      setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }])
    } finally {
      setIsStreaming(false)
    }
  }

  const renderComponent = (component: { name: string; props: any }) => {
    switch (component.name) {
      case 'StockCard':
        return <StockCard {...component.props} />
      case 'WeatherCard':
        return <WeatherCard {...component.props} />
      case 'FlightCard':
        return <FlightCard {...component.props} />
      case 'RecipeCard':
        return <RecipeCard {...component.props} />
      case 'MovieCard':
        return <MovieCard {...component.props} />
      case 'ProductCard':
        return <ProductCard {...component.props} />
      case 'HotelCard':
        return <HotelCard {...component.props} />
      case 'RestaurantCard':
        return <RestaurantCard {...component.props} />
      case 'BookCard':
        return <BookCard {...component.props} />
      case 'NewsCard':
        return <NewsCard {...component.props} />
      case 'EventCard':
        return <EventCard {...component.props} />
      case 'ExerciseCard':
        return <ExerciseCard {...component.props} />
      default:
        return null
    }
  }

  // Render markdown with custom styling
  const renderMarkdown = (text: string, isUserMessage: boolean = false) => {
    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          // Links - open in new tab
          a: ({ node, ...props }) => (
            <a
              {...props}
              target="_blank"
              rel="noopener noreferrer"
              className={
                isUserMessage
                  ? 'text-blue-200 hover:text-white underline break-all font-semibold'
                  : 'text-blue-600 hover:text-blue-800 underline break-all font-semibold'
              }
            />
          ),
          // Headings
          h1: ({ node, ...props }) => <h1 {...props} className="text-2xl font-bold mt-4 mb-2" />,
          h2: ({ node, ...props }) => <h2 {...props} className="text-xl font-bold mt-3 mb-2" />,
          h3: ({ node, ...props }) => <h3 {...props} className="text-lg font-bold mt-2 mb-1" />,
          // Bold text
          strong: ({ node, ...props }) => <strong {...props} className="font-bold" />,
          // Lists
          ul: ({ node, ...props }) => <ul {...props} className="list-disc list-inside my-2 space-y-1" />,
          ol: ({ node, ...props }) => <ol {...props} className="list-decimal list-inside my-2 space-y-1" />,
          li: ({ node, ...props }) => <li {...props} className="ml-4" />,
          // Tables
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table {...props} className="min-w-full divide-y divide-gray-200 border border-gray-300" />
            </div>
          ),
          thead: ({ node, ...props }) => <thead {...props} className="bg-gray-50" />,
          tbody: ({ node, ...props }) => <tbody {...props} className="bg-white divide-y divide-gray-200" />,
          tr: ({ node, ...props }) => <tr {...props} />,
          th: ({ node, ...props }) => (
            <th {...props} className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border border-gray-300" />
          ),
          td: ({ node, ...props }) => (
            <td {...props} className="px-4 py-2 text-sm text-gray-900 border border-gray-300" />
          ),
          // Code blocks
          code: ({ node, inline, ...props }: any) =>
            inline ? (
              <code {...props} className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm font-mono" />
            ) : (
              <code {...props} className="block bg-gray-900 text-gray-100 p-3 rounded my-2 overflow-x-auto text-sm font-mono" />
            ),
          pre: ({ node, ...props }) => <pre {...props} className="my-2" />,
          // Blockquotes
          blockquote: ({ node, ...props }) => (
            <blockquote {...props} className="border-l-4 border-gray-300 pl-4 italic my-2 text-gray-700" />
          ),
          // Paragraphs
          p: ({ node, ...props }) => <p {...props} className="my-1" />,
        }}
      >
        {text}
      </ReactMarkdown>
    )
  }

  const sampleQueries = [
    { icon: '📈', label: '주식 정보', query: '애플 주식 가격 알려줘' },
    { icon: '🌤️', label: '날씨', query: '서울 날씨 알려줘' },
    { icon: '✈️', label: '항공편', query: 'KE001 항공편 정보 알려줘' },
    { icon: '🍳', label: '레시피', query: '파스타 레시피 알려줘' },
    { icon: '🎬', label: '영화', query: '쇼생크 탈출 영화 정보 알려줘' },
    { icon: '🛍️', label: '상품', query: '헤드폰 추천해줘' },
    { icon: '🏨', label: '호텔', query: '서울 호텔 추천해줘' },
    { icon: '🍽️', label: '맛집', query: '맛집 추천해줘' },
    { icon: '📚', label: '도서', query: '읽을만한 책 추천해줘' },
    { icon: '📰', label: '뉴스', query: '최신 기술 뉴스 알려줘' },
    { icon: '🎫', label: '이벤트', query: '이벤트 정보 알려줘' },
    { icon: '💪', label: '운동', query: '운동 루틴 알려줘' },
  ]

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              Agent Framework + Generative UI
            </h1>
            <p className="text-sm text-gray-500">
              Ollama & FastAPI 기반 생성형 UI 챗봇
            </p>
          </div>
          <div className="flex items-center gap-3">
            <MCPSettings />
            <ModelSelector
              onModelChange={(model) => {
                console.log('모델 변경:', model)
              }}
            />
          </div>
        </div>

        {/* Sample Query Buttons - Always Visible */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {sampleQueries.map((sample, index) => (
            <button
              key={index}
              onClick={() => setInput(sample.query)}
              className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-blue-50 hover:border-blue-300 transition-colors"
              disabled={isStreaming}
            >
              <span className="mr-1">{sample.icon}</span>
              {sample.label}
            </button>
          ))}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              안녕하세요! 무엇을 도와드릴까요?
            </h2>
            <p className="text-gray-500">
              위의 버튼을 클릭하거나 직접 질문을 입력해보세요
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={cn(
              'flex',
              message.role === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            <div
              className={cn(
                'max-w-[80%] rounded-lg px-4 py-3',
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white border'
              )}
            >
              {message.components && message.components.length > 0 && (
                <div className="space-y-3 mb-3">
                  {message.components.map((component, idx) => (
                    <div key={idx}>{renderComponent(component)}</div>
                  ))}
                </div>
              )}
              {message.content && (
                <div className="prose prose-sm max-w-none">
                  {renderMarkdown(message.content, message.role === 'user')}
                </div>
              )}
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            전송
          </button>
        </form>
      </div>
    </div>
  )
}
