'use client'

import { useEffect, useState } from 'react'
import { Settings, Server, RefreshCw, Power, PowerOff } from 'lucide-react'

interface MCPServer {
  name: string
  enabled: boolean
  description: string
  command: string
}

export function MCPSettings() {
  const [isOpen, setIsOpen] = useState(false)
  const [servers, setServers] = useState<MCPServer[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchServers()
    }
  }, [isOpen])

  const fetchServers = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/mcp/servers`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setServers(data.servers || [])
    } catch (error) {
      console.error('Failed to fetch MCP servers:', error)
      setError('서버 목록을 불러올 수 없습니다')
      setServers([])
    } finally {
      setIsLoading(false)
    }
  }

  const toggleServer = async (serverName: string, currentlyEnabled: boolean) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/mcp/servers/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          server_name: serverName,
          enabled: !currentlyEnabled,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to toggle server')
      }

      // 서버 목록 새로고침
      await fetchServers()
    } catch (error) {
      console.error('Failed to toggle server:', error)
      setError(`서버 ${serverName} 상태 변경 실패`)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors"
        title="MCP Settings"
      >
        <Server className="w-5 h-5 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">MCP</span>
      </button>
    )
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={() => setIsOpen(false)}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold">MCP Server Settings</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchServers}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh"
                disabled={isLoading}
              >
                <RefreshCw
                  className={`w-5 h-5 text-gray-600 ${
                    isLoading ? 'animate-spin' : ''
                  }`}
                />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <span className="text-2xl text-gray-600">&times;</span>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            {isLoading && servers.length === 0 ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : servers.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Server className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>사용 가능한 MCP 서버가 없습니다</p>
              </div>
            ) : (
              <div className="space-y-3">
                {servers.map((server) => (
                  <div
                    key={server.name}
                    className="border rounded-lg p-4 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-lg">
                            {server.name}
                          </h3>
                          {server.enabled && (
                            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                              Active
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {server.description}
                        </p>
                        <p className="text-xs text-gray-400 font-mono">
                          {server.command}
                        </p>
                      </div>

                      <button
                        onClick={() => toggleServer(server.name, server.enabled)}
                        className={`ml-4 p-2 rounded-lg transition-colors ${
                          server.enabled
                            ? 'bg-green-100 hover:bg-green-200 text-green-700'
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                        }`}
                        title={server.enabled ? 'Disable' : 'Enable'}
                      >
                        {server.enabled ? (
                          <Power className="w-5 h-5" />
                        ) : (
                          <PowerOff className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t bg-gray-50">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                {servers.filter((s) => s.enabled).length} / {servers.length}{' '}
                서버 활성화
              </span>
              <a
                href="https://modelcontextprotocol.io"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                MCP 문서 보기 →
              </a>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
