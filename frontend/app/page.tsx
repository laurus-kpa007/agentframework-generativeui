'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
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
import { cn } from '@/lib/utils'

interface Message {
  role: 'user' | 'assistant'
  content: string
  component?: {
    name: string
    props: any
  }
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

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
      for await (const event of apiClient.streamChat(userMessage)) {
        if (event.type === 'text') {
          assistantMessage.content += event.content
          setMessages((prev) => [
            ...prev.slice(0, -1),
            { ...assistantMessage },
          ])
        } else if (event.type === 'component') {
          assistantMessage.component = {
            name: event.component!,
            props: event.props,
          }
          setMessages((prev) => [
            ...prev.slice(0, -1),
            { ...assistantMessage },
          ])
        } else if (event.type === 'error') {
          console.error('Stream error:', event.message)
        }
      }
    } catch (error) {
      console.error('Failed to stream chat:', error)
      assistantMessage.content =
        'Sorry, I encountered an error. Please try again.'
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
              Powered by Ollama & FastAPI
            </p>
          </div>
          <ModelSelector
            onModelChange={(model) => {
              console.log('Model changed to:', model)
              // Optionally clear conversation when model changes
              // setMessages([])
            }}
          />
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-700 mb-2">
              Welcome! How can I help you today?
            </h2>
            <p className="text-gray-500">
              Try asking about stocks, weather, or flights
            </p>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-w-4xl mx-auto">
              <button
                onClick={() => setInput('Show me AAPL stock price')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                📈 Stock Info
              </button>
              <button
                onClick={() => setInput('Weather in Seoul')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🌤️ Weather
              </button>
              <button
                onClick={() => setInput('Show flight KE001')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                ✈️ Flight
              </button>
              <button
                onClick={() => setInput('Show me a recipe for pasta')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🍳 Recipe
              </button>
              <button
                onClick={() => setInput('Tell me about the movie Shawshank')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🎬 Movie
              </button>
              <button
                onClick={() => setInput('Show me headphones to buy')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🛍️ Product
              </button>
              <button
                onClick={() => setInput('Find a hotel in Seoul')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🏨 Hotel
              </button>
              <button
                onClick={() => setInput('Recommend a restaurant')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🍽️ Restaurant
              </button>
              <button
                onClick={() => setInput('Show me a book to read')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                📚 Book
              </button>
              <button
                onClick={() => setInput('Latest tech news')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                📰 News
              </button>
              <button
                onClick={() => setInput('Show me events')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                🎫 Event
              </button>
              <button
                onClick={() => setInput('Give me a workout routine')}
                className="px-3 py-2 bg-white border rounded-lg text-xs hover:bg-gray-50 transition-colors"
              >
                💪 Exercise
              </button>
            </div>
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
              {message.component && (
                <div className="mb-3">{renderComponent(message.component)}</div>
              )}
              {message.content && (
                <p className="whitespace-pre-wrap">{message.content}</p>
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
      </div>

      {/* Input */}
      <div className="bg-white border-t px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
