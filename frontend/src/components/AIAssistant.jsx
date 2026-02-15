import { useState } from 'react'

function AIAssistant({ code, error, language, onCodeUpdate }) {
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastAction, setLastAction] = useState(null)
  const [codeApplied, setCodeApplied] = useState(false)

  // Extract code block from AI response
  const extractCodeBlock = (text) => {
    if (!text) return null
    // Match ```language\n...\n``` or ```\n...\n```
    const patterns = [
      /```(?:\w+)?\s*\n([\s\S]*?)```/g,
    ]
    let lastMatch = null
    for (const pattern of patterns) {
      let match
      while ((match = pattern.exec(text)) !== null) {
        lastMatch = match[1].trim()
      }
    }
    return lastMatch
  }

  const handleAIAction = async (actionType) => {
    setLastAction(actionType)
    setLoading(true)
    setResponse(null)
    setCodeApplied(false)

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

        // Auto-apply fix for fix_error and optimize_code
        if ((actionType === 'fix_error' || actionType === 'optimize_code') && onCodeUpdate) {
          const extracted = extractCodeBlock(data.response)
          if (extracted) {
            onCodeUpdate(extracted)
            setCodeApplied(true)
          }
        }
      } else {
        setResponse(`Error: ${data.error || 'AI request failed'}`)
      }
    } catch (err) {
      setResponse(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyCode = () => {
    if (!response || !onCodeUpdate) return
    const extracted = extractCodeBlock(response)
    if (extracted) {
      onCodeUpdate(extracted)
      setCodeApplied(true)
    }
  }

  const hasError = !!error
  const hasCode = !!code
  const hasExtractableCode = response ? !!extractCodeBlock(response) : false

  const actions = [
    { id: 'fix_error', label: 'Fix Error', disabled: !hasError },
    { id: 'explain_error', label: 'Explain Error', disabled: !hasError },
    { id: 'explain_code', label: 'Explain Code', disabled: !hasCode },
    { id: 'optimize_code', label: 'Optimize', disabled: !hasCode },
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
            className={`px-3 py-1 text-xs rounded transition-colors ${
              loading || action.disabled
                ? 'text-[#585858] cursor-not-allowed'
                : 'text-[#cccccc] hover:bg-[#3a3a3a] hover:text-white'
            }`}
            title={action.disabled ? (action.id.includes('error') ? 'Run code with an error first' : 'Write some code first') : action.label}
          >
            {action.label}
          </button>
        ))}

        <div className="ml-auto flex items-center gap-2">
          {/* Apply Code button */}
          {hasExtractableCode && !codeApplied && !loading && (
            <button
              onClick={handleApplyCode}
              className="px-2 py-0.5 text-xs bg-[#0e639c] hover:bg-[#1177bb] text-white rounded transition-colors"
            >
              Apply Code
            </button>
          )}
          
          {codeApplied && (
            <span className="text-xs text-[#608b4e]">✓ Applied</span>
          )}

          {loading && (
            <span className="text-xs text-[#858585] flex items-center gap-1.5">
              <svg className="animate-spin w-3 h-3" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="20 10"/>
              </svg>
              Processing...
            </span>
          )}

          {response && !loading && (
            <button onClick={() => { setResponse(null); setCodeApplied(false) }}
              className="text-xs text-[#858585] hover:text-white transition-colors">
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Response Area */}
      <div className="flex-1 overflow-y-auto">
        {response ? (
          <div className="p-3">
            {codeApplied && (
              <div className="mb-2 px-2 py-1 bg-[#2b4c2b] rounded text-xs text-[#608b4e]">
                ✓ Fixed code has been applied to the editor
              </div>
            )}
            <pre className="whitespace-pre-wrap text-[13px] text-[#d4d4d4] font-[Consolas,'Courier_New',monospace] leading-relaxed">
              {response}
            </pre>
          </div>
        ) : !loading ? (
          <div className="flex items-center justify-center h-full text-xs text-[#585858]">
            {hasError 
              ? 'Click "Fix Error" to auto-fix your code, or "Explain Error" for details'
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
