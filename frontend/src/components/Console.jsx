import { useEffect, useRef, useMemo } from 'react'

// ANSI color code to CSS color mapping
const ANSI_COLORS = {
  '30': '#585858', '31': '#f44747', '32': '#608b4e', '33': '#dcdcaa',
  '34': '#569cd6', '35': '#c586c0', '36': '#4ec9b0', '37': '#d4d4d4',
  '90': '#6a6a6a', '91': '#f47070', '92': '#73c991', '93': '#e8e8a0',
  '94': '#7cb3f0', '95': '#d0a0e0', '96': '#70dcc8', '97': '#ffffff',
}

function parseAnsi(text) {
  if (!text) return [{ text: '', style: {} }]
  const parts = []
  let currentStyle = {}
  const regex = /\x1b\[([0-9;]*)m/g
  let lastIndex = 0
  let match
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ text: text.slice(lastIndex, match.index), style: { ...currentStyle } })
    }
    const codes = match[1].split(';').filter(Boolean)
    if (codes.length === 0 || (codes.length === 1 && codes[0] === '0') || match[1] === '') {
      currentStyle = {}
    } else {
      for (const code of codes) {
        if (code === '0') currentStyle = {}
        else if (code === '1') currentStyle = { ...currentStyle, fontWeight: 'bold' }
        else if (ANSI_COLORS[code]) currentStyle = { ...currentStyle, color: ANSI_COLORS[code] }
      }
    }
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < text.length) {
    parts.push({ text: text.slice(lastIndex), style: { ...currentStyle } })
  }
  return parts.length > 0 ? parts : [{ text, style: {} }]
}

function AnsiText({ text }) {
  const parts = useMemo(() => parseAnsi(text), [text])
  return (
    <span>
      {parts.map((part, i) => (
        <span key={i} style={part.style}>{part.text}</span>
      ))}
    </span>
  )
}

function Console({ output, isRunning, onClear, onInstallAndRerun, isInstalling }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [output])

  const getMessageColor = (type) => {
    switch (type) {
      case 'status': return '#569cd6'
      case 'stderr': case 'error': return '#f44747'
      case 'complete': return '#608b4e'
      case 'dependency': return '#dcdcaa'
      case 'install_start': return '#569cd6'
      case 'install_complete': return '#608b4e'
      case 'install_error': return '#f44747'
      default: return null
    }
  }

  const getPrefix = (type) => {
    switch (type) {
      case 'status': case 'complete': return '› '
      case 'dependency': return '⚠ '
      default: return ''
    }
  }

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

          const isFailComplete = msg.type === 'complete' && msg.content?.includes('failed')
          const fixedColor = isFailComplete ? '#f44747' : getMessageColor(msg.type)
          const prefix = getPrefix(msg.type)

          if (fixedColor) {
            return (
              <div key={i} className="whitespace-pre-wrap break-all" style={{ color: fixedColor }}>
                {prefix}{msg.content}
              </div>
            )
          }

          return (
            <div key={i} className="whitespace-pre-wrap break-all text-[#d4d4d4]">
              {prefix}<AnsiText text={msg.content} />
            </div>
          )
        })}

        {isRunning && !isInstalling && (
          <div className="flex items-center gap-2" style={{ color: '#569cd6' }}>
            <span className="animate-pulse">●</span> Running...
          </div>
        )}

        {showInstallButton && (
          <div className="mt-3 p-3 rounded bg-[#2d2a1e] border border-[#665c33]">
            <div className="flex items-center justify-between gap-3">
              <div className="flex-1">
                <div className="text-xs font-semibold mb-1" style={{ color: '#dcdcaa' }}>
                  📦 Missing Package: {dependencyMsg.package_name}
                </div>
                <div className="text-xs" style={{ color: '#858585' }}>
                  Click to install <span style={{ color: '#ce9178' }}>{dependencyMsg.package_name}</span> and re-run your code automatically
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

        {isInstalling && (
          <div className="flex items-center gap-2 mt-1" style={{ color: '#569cd6' }}>
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
