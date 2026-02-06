import { useEffect, useRef } from 'react'

function Console({ output = [], isRunning = false, onClear }) {
  const consoleEndRef = useRef(null)

  // Auto-scroll to bottom when new output arrives
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [output])

  const getMessageStyle = (type) => {
    switch (type) {
      case 'stdout':
        return 'text-gray-200'
      case 'stderr':
        return 'text-red-400'
      case 'error':
        return 'text-red-500 font-semibold'
      case 'status':
        return 'text-blue-400 italic'
      case 'complete':
        return 'text-green-400'
      default:
        return 'text-gray-300'
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-800 rounded-lg border border-gray-700">
      {/* Console Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-300">Console</h3>
          {isRunning && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400">Running...</span>
            </div>
          )}
        </div>
        
        <button
          onClick={onClear}
          className="text-xs text-gray-400 hover:text-white transition-colors"
          title="Clear console"
        >
          Clear
        </button>
      </div>

      {/* Console Output */}
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
        {output.length === 0 ? (
          <div className="text-gray-500 text-sm">
            Output will appear here...
          </div>
        ) : (
          <>
            {output.map((msg, index) => (
              <div key={index} className={`mb-1 ${getMessageStyle(msg.type)}`}>
                {msg.type === 'status' && <span className="text-gray-500">[{msg.timestamp}] </span>}
                <span className="whitespace-pre-wrap break-words">{msg.content}</span>
              </div>
            ))}
            <div ref={consoleEndRef} />
          </>
        )}
      </div>
    </div>
  )
}

export default Console
