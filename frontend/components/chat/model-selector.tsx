'use client'

import { useState, useEffect } from 'react'
import { Check, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Model {
  name: string
  size: string
  modified_at: string
}

interface ModelSelectorProps {
  onModelChange?: (model: string) => void
}

export function ModelSelector({ onModelChange }: ModelSelectorProps) {
  const [models, setModels] = useState<Model[]>([])
  const [currentModel, setCurrentModel] = useState<string>('')
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/models/list`)
      const data = await response.json()

      setModels(data.models)
      setCurrentModel(data.current_model)
    } catch (error) {
      console.error('Failed to fetch models:', error)
    }
  }

  const selectModel = async (modelName: string) => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/models/select`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model: modelName }),
      })

      if (response.ok) {
        setCurrentModel(modelName)
        setIsOpen(false)
        onModelChange?.(modelName)
      }
    } catch (error) {
      console.error('Failed to select model:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatModelName = (name: string) => {
    // Remove :latest or other tags for display
    if (!name) return 'Select Model'
    return name.split(':')[0]
  }

  const formatSize = (size: string) => {
    if (!size || size === 'unknown') return ''

    const bytes = parseInt(size)
    if (isNaN(bytes)) return size

    const gb = bytes / (1024 ** 3)
    return `(${gb.toFixed(1)} GB)`
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className={cn(
          'flex items-center gap-2 px-3 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50 transition-colors',
          isLoading && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span className="font-medium">{formatModelName(currentModel)}</span>
        <ChevronDown
          className={cn(
            'w-4 h-4 transition-transform',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-64 bg-white border rounded-lg shadow-lg z-20 max-h-80 overflow-y-auto">
            <div className="p-2">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Available Models
              </div>

              {models.length === 0 ? (
                <div className="px-3 py-4 text-sm text-gray-500 text-center">
                  No models found
                </div>
              ) : (
                models.map((model) => (
                  <button
                    key={model.name}
                    onClick={() => selectModel(model.name)}
                    className={cn(
                      'w-full flex items-center justify-between px-3 py-2 rounded-lg text-left text-sm hover:bg-gray-100 transition-colors',
                      currentModel === model.name && 'bg-blue-50'
                    )}
                  >
                    <div className="flex-1">
                      <div className="font-medium">
                        {formatModelName(model.name)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatSize(model.size)}
                      </div>
                    </div>

                    {currentModel === model.name && (
                      <Check className="w-4 h-4 text-blue-600" />
                    )}
                  </button>
                ))
              )}
            </div>

            <div className="border-t p-2">
              <button
                onClick={fetchModels}
                className="w-full px-3 py-2 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Refresh Models
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
