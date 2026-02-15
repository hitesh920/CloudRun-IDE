import { useState, useEffect, useRef } from 'react'

function Console({ output = [], isRunning = false, onClear }) {
  const consoleEndRef = useRef(null)
  const [htmlPreview, setHtmlPreview] = useState(null)

  // Auto-scroll to bottom when new output arrives
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [output])

  // Detect HTML preview messages
  useEffect(() => {
    const previewMsg = output.find(msg => msg.type === 'html_preview')
    if (previewMsg) {
      setHtmlPreview(previewMsg.content)
    }
  }, [output])

  // Clear preview when output is cleared
  useEffect(() => {
    if (output.length === 0) {
      setHtmlPreview(null)
    }
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
      case 'dependency':
        return 'text-yellow-400'
      case 'html_preview':
        return 'hidden'  // Hide the raw HTML message
      default:
        return 'text-gray-300'
    }
  }

  const getPrefix = (type) => {
    switch (type) {
      case 'status':
        return '⚡ '
      case 'error':
        return '❌ '
      case 'complete':
        return '✅ '
      case 'dependency':
        return '📦 '
      default:
        return ''
    }
  }

  const handleClear = () => {
    setHtmlPreview(null)
    onClear()
  }

  return (
    <div className="h-full flex flex-col bg-gray-800 rounded-lg border border-gray-700">
      {/* Console Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-300">
            {htmlPreview ? 'Preview' : 'Console'}
          </h3>
          {isRunning && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-400">Running...</span>
            </div>
          )}
        </div>
        
        <button
          onClick={handleClear}
          className="text-xs text-gray-400 hover:text-white transition-colors"
          title="Clear console (Ctrl+K)"
        >
          Clear
        </button>
      </div>

      {/* HTML Preview */}
      {htmlPreview ? (
        <div className="flex-1 bg-white rounded-b-lg overflow-hidden">
          <iframe
            srcDoc={htmlPreview}
            title="HTML Preview"
            className="w-full h-full border-0"
            sandbox="allow-scripts allow-modals"
          />
        </div>
      ) : (
        /* Console Output */
        <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
          {output.length === 0 ? (
            <div className="text-gray-500 text-sm">
              Output will appear here...
              <br />
              <span className="text-xs text-gray-600 mt-2 block">
                Press Ctrl+Enter to run code
              </span>
            </div>
          ) : (
            <>
              {output.map((msg, index) => (
                <div key={index} className={`mb-1 ${getMessageStyle(msg.type)}`}>
                  <span className="whitespace-pre-wrap break-words">
                    {getPrefix(msg.type)}{msg.content}
                  </span>
                </div>
              ))}
              <div ref={consoleEndRef} />
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default Console
