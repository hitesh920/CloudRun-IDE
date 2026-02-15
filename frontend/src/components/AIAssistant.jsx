import { useState } from 'react'
import { Sparkles, X, Loader } from 'lucide-react'

function AIAssistant({ code, error, language, onClose }) {
  const [action, setAction] = useState(null)
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(true)

  const handleAIAction = async (actionType) => {
    setAction(actionType)
    setLoading(true)
    setResponse(null)

    try {
      const payload = {
        action: actionType,
        language,
      }

      if (actionType === 'fix_error') {
        payload.code = code
        payload.error = error
      } else if (actionType === 'explain_error') {
        payload.error = error
      } else if (actionType === 'explain_code' || actionType === 'optimize_code') {
        payload.code = code
      }

      const res = await fetch('/api/ai/assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (data.success) {
        setResponse(data.response)
      } else {
        setResponse(`Error: ${data.error || 'AI request failed'}`)
      }
    } catch (err) {
      setResponse(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-purple-500/30 overflow-hidden">
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-b border-gray-700 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-sm font-semibold text-gray-200">AI Assistant</span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-gray-500 text-sm">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-4">
          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <button
              onClick={() => handleAIAction('fix_error')}
              disabled={loading || !error}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm transition-colors"
            >
              Fix Error
            </button>
            
            <button
              onClick={() => handleAIAction('explain_error')}
              disabled={loading || !error}
              className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm transition-colors"
            >
              Explain Error
            </button>
            
            <button
              onClick={() => handleAIAction('explain_code')}
              disabled={loading || !code}
              className="px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm transition-colors"
            >
              Explain Code
            </button>
            
            <button
              onClick={() => handleAIAction('optimize_code')}
              disabled={loading || !code}
              className="px-3 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm transition-colors"
            >
              Optimize Code
            </button>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-3">
              <Loader className="w-4 h-4 animate-spin" />
              <span>Asking AI...</span>
            </div>
          )}

          {/* AI Response */}
          {response && (
            <div className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
              <div className="prose prose-invert prose-sm max-w-none">
                <pre className="whitespace-pre-wrap text-gray-300 text-sm font-sans">
                  {response}
                </pre>
              </div>
            </div>
          )}

          {/* Help Text */}
          {!loading && !response && (
            <div className="text-xs text-gray-500 text-center">
              {error ? 'Click a button to get AI assistance' : 'Run code first to get assistance'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AIAssistant
