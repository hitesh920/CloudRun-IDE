import { useState } from 'react'

function InputPanel({ onInputChange, disabled = false }) {
  const [input, setInput] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)

  const handleChange = (e) => {
    const value = e.target.value
    setInput(value)
    if (onInputChange) {
      onInputChange(value)
    }
  }

  const handleClear = () => {
    setInput('')
    if (onInputChange) {
      onInputChange('')
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-2 bg-gray-750 border-b border-gray-700 cursor-pointer hover:bg-gray-700 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-300">Input (stdin)</span>
          {input && !isExpanded && (
            <span className="text-xs text-gray-500">
              ({input.split('\n').length} line{input.split('\n').length !== 1 ? 's' : ''})
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {input && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleClear()
              }}
              className="text-xs text-gray-400 hover:text-white transition-colors"
              disabled={disabled}
            >
              Clear
            </button>
          )}
          <span className="text-gray-500 text-sm">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* Input Area */}
      {isExpanded && (
        <div className="p-3">
          <textarea
            value={input}
            onChange={handleChange}
            disabled={disabled}
            placeholder="Enter input for your program here (one value per line)..."
            className="w-full h-32 bg-gray-900 text-gray-200 font-mono text-sm p-3 rounded border border-gray-700 
                     focus:outline-none focus:border-blue-500 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <div className="mt-2 text-xs text-gray-500">
            💡 Tip: Each line will be passed as input when your program calls input() or scanf()
          </div>
        </div>
      )}
    </div>
  )
}

export default InputPanel
