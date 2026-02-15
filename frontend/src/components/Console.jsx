import { useEffect, useRef } from 'react'

function Console({ output, isRunning, onClear, onInstallAndRerun, isInstalling }) {
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
      case 'complete': return 'text-[#608b4e]'
      case 'dependency': return 'text-[#dcdcaa]'
      case 'install_start': return 'text-[#569cd6]'
      case 'install_complete': return 'text-[#608b4e]'
      case 'install_error': return 'text-[#f44747]'
      case 'html_preview': return ''
      default: return 'text-[#d4d4d4]'
    }
  }

  const getPrefix = (type) => {
    switch (type) {
      case 'status': return '› '
      case 'complete': return '› '
      case 'dependency': return '⚠ '
      case 'install_start': return '📦 '
      case 'install_complete': return '✅ '
      case 'install_error': return '❌ '
      default: return ''
    }
  }

  // Find if there's a detected dependency in the output
  const dependencyMsg = output.find(m => m.type === 'dependency')
  const isComplete = output.some(m => m.type === 'complete')
  const showInstallButton = dependencyMsg && isComplete && !isRunning && !isInstalling

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e] overflow-hidden">
      <div className="flex items-center justify-end px-3 py-1 flex-shrink-0 bg-[#252526] border-b border-[#1e1e1e]">
        <button onClick={onClear} className="text-[11px] text-[#858585] hover:text-white transition-colors">Clear</button>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 font-[Consolas,'Courier_New',monospace] text-[13px] leading-5">
        {output.length === 0 && !isRunning && (
          <div className="text-[#585858] text-xs">Terminal ready. Click Run to execute code.</div>
        )}

        {output.map((msg, i) => {
          if (msg.type === 'html_preview') {
            return (
              <div key={i} className="my-2">
                <iframe srcDoc={msg.content} className="w-full bg-white rounded"
                  style={{ height: '300px', border: '1px solid #414141' }}
                  title="HTML Preview" sandbox="allow-scripts allow-modals" />
              </div>
            )
          }

          const isError = msg.type === 'complete' && msg.content?.includes('failed')

          return (
            <div key={i} className={`${isError ? 'text-[#f44747]' : getMessageStyle(msg.type)} whitespace-pre-wrap break-all`}>
              {getPrefix(msg.type)}{msg.content}
            </div>
          )
        })}

        {isRunning && !isInstalling && (
          <div className="text-[#569cd6] flex items-center gap-2">
            <span className="animate-pulse">●</span> Running...
          </div>
        )}

        {/* Install & Re-run Banner */}
        {showInstallButton && (
          <div className="mt-3 p-3 rounded bg-[#2d2a1e] border border-[#665c33]">
            <div className="flex items-center justify-between gap-3">
              <div className="flex-1">
                <div className="text-[#dcdcaa] text-xs font-semibold mb-1">
                  📦 Missing Package: {dependencyMsg.package_name}
                </div>
                <div className="text-[#858585] text-xs">
                  Click to install <span className="text-[#ce9178]">{dependencyMsg.package_name}</span> and re-run your code automatically
                </div>
              </div>
              <button
                onClick={() => onInstallAndRerun && onInstallAndRerun([dependencyMsg.package_name])}
                className="px-4 py-1.5 text-xs font-medium bg-[#0e639c] hover:bg-[#1177bb] text-white rounded transition-colors whitespace-nowrap"
              >
                Install &amp; Re-run
              </button>
            </div>
          </div>
        )}

        {/* Installing indicator */}
        {isInstalling && (
          <div className="text-[#569cd6] flex items-center gap-2 mt-1">
            <svg className="animate-spin w-3 h-3" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="2" strokeDasharray="20 10"/>
            </svg>
            Installing packages...
          </div>
        )}
      </div>
    </div>
  )
}

export default Console
