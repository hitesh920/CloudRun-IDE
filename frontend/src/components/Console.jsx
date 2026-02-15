import { useEffect, useRef } from 'react'

function Console({ output, isRunning, onClear }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [output])

  const getMessageStyle = (type) => {
    switch (type) {
      case 'status': return 'text-[#569cd6]'
      case 'stdout': return 'text-[#d4d4d4]'
      case 'stderr': return 'text-[#f44747]'
      case 'error': return 'text-[#f44747]'
      case 'complete':
        return 'text-[#608b4e]'
      case 'html_preview': return ''
      default: return 'text-[#d4d4d4]'
    }
  }

  const getPrefix = (type) => {
    switch (type) {
      case 'status': return '› '
      case 'stderr': return ''
      case 'error': return ''
      case 'complete': return '› '
      default: return ''
    }
  }

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e] overflow-hidden">
      {/* Console toolbar */}
      <div className="flex items-center justify-end px-3 py-1 flex-shrink-0 bg-[#252526] border-b border-[#1e1e1e]">
        <button
          onClick={onClear}
          className="text-[11px] text-[#858585] hover:text-white transition-colors"
          title="Clear console"
        >
          Clear
        </button>
      </div>

      {/* Output area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 font-[Consolas,'Courier_New',monospace] text-[13px] leading-5">
        {output.length === 0 && !isRunning && (
          <div className="text-[#585858] text-xs">
            Terminal ready. Click Run to execute code.
          </div>
        )}

        {output.map((msg, i) => {
          // HTML preview
          if (msg.type === 'html_preview') {
            return (
              <div key={i} className="my-2">
                <iframe
                  srcDoc={msg.content}
                  className="w-full bg-white rounded"
                  style={{ height: '300px', border: '1px solid #414141' }}
                  title="HTML Preview"
                  sandbox="allow-scripts allow-modals"
                />
              </div>
            )
          }

          const isError = msg.type === 'complete' && msg.content?.includes('failed')

          return (
            <div 
              key={i} 
              className={`${isError ? 'text-[#f44747]' : getMessageStyle(msg.type)} whitespace-pre-wrap break-all`}
            >
              {getPrefix(msg.type)}{msg.content}
            </div>
          )
        })}

        {isRunning && (
          <div className="text-[#569cd6] flex items-center gap-2">
            <span className="animate-pulse">●</span>
            <span>Running...</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default Console
