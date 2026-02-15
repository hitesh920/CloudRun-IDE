import { useState } from 'react'

function AIAssistant({ code, error, language }) {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastAction, setLastAction] = useState(null)

  const handleAIAction = async (actionType) => {
    setLastAction(actionType)
    setLoading(true)
    setResponse(null)

    try {
      const payload = { action: actionType, language }

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

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }

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

  const hasError = !!error
  const hasCode = !!code

  const actions = [
    { id: 'fix_error', label: 'Fix Error', disabled: !hasError, icon: '🔧' },
    { id: 'explain_error', label: 'Explain Error', disabled: !hasError, icon: '❓' },
    { id: 'explain_code', label: 'Explain Code', disabled: !hasCode, icon: '📖' },
    { id: 'optimize_code', label: 'Optimize', disabled: !hasCode, icon: '⚡' },
  ]

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e] overflow-hidden">
      {/* Action Buttons Row */}
      <div className="flex items-center gap-1 px-3 py-2 bg-[#252526] border-b border-[#1e1e1e] flex-shrink-0">
        {actions.map(action => (
          <button
            key={action.id}
            onClick={() => handleAIAction(action.id)}
            disabled={loading || action.disabled}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs rounded transition-colors ${
              loading || action.disabled
                ? 'text-[#585858] cursor-not-allowed'
                : 'text-[#cccccc] hover:bg-[#3a3a3a] hover:text-white'
            }`}
            title={action.disabled ? (action.id.includes('error') ? 'Run code with an error first' : 'Write some code first') : action.label}
          >
            <span className="text-[10px]">{action.icon}</span>
            {action.label}
          </button>
        ))}

        {/* Loading indicator */}
        {loading && (
          <span className="text-xs text-[#858585] ml-auto flex items-center gap-1.5">
            <svg className="animate-spin w-3 h-3" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="20 10"/>
            </svg>
            Processing...
          </span>
        )}

        {/* Clear button */}
        {response && !loading && (
          <button
            onClick={() => setResponse(null)}
            className="text-xs text-[#858585] hover:text-white ml-auto transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {/* Response Area */}
      <div className="flex-1 overflow-y-auto">
        {response ? (
          <div className="p-3">
            <pre className="whitespace-pre-wrap text-[13px] text-[#d4d4d4] font-[Consolas,'Courier_New',monospace] leading-relaxed">
              {response}
            </pre>
          </div>
        ) : !loading ? (
          <div className="flex items-center justify-center h-full text-xs text-[#585858]">
            {hasError 
              ? 'Click "Fix Error" or "Explain Error" to get AI help'
              : hasCode 
                ? 'Click "Explain Code" or "Optimize" to get AI analysis'
                : 'Write and run code to use AI assistance'
            }
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default AIAssistant
