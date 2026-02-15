import { useState, useEffect, useRef, useCallback } from 'react'
import { CodeEditor, LANGUAGE_CONFIGS } from './components/Editor'
import Console from './components/Console'
import InputPanel from './components/InputPanel'
import FileExplorer from './components/FileExplorer'
import AIAssistant from './components/AIAssistant'
import AuthScreen from './components/AuthScreen'
import { useWebSocket } from './hooks/useWebSocket'
import { useTheme } from './hooks/useTheme'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'
import authService from './services/auth'

function App() {
  const [currentView, setCurrentView] = useState('loading')
  const [selectedLanguage, setSelectedLanguage] = useState(null)
  const [user, setUser] = useState(null)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isLoggedIn) {
        const valid = await authService.verify()
        if (valid) {
          setUser(authService.user)
          setCurrentView('welcome')
          return
        }
      }
      setCurrentView('auth')
    }
    checkAuth()
  }, [])

  const handleAuthSuccess = (userData) => {
    setUser(userData)
    setCurrentView('welcome')
  }

  const handleSkipAuth = () => {
    setUser(null)
    setCurrentView('welcome')
  }

  const handleLogout = () => {
    authService.logout()
    setUser(null)
    setCurrentView('auth')
  }

  if (currentView === 'loading') {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#1e1e1e]">
        <div className="text-[#858585] text-sm">Loading...</div>
      </div>
    )
  }

  if (currentView === 'auth') {
    return (
      <div className="h-screen w-screen flex flex-col bg-[#1e1e1e] text-[#cccccc]">
        <AuthScreen onAuthSuccess={handleAuthSuccess} onSkip={handleSkipAuth} />
      </div>
    )
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-[#1e1e1e] text-[#cccccc]">
      {currentView === 'welcome' ? (
        <WelcomeScreen user={user}
          onLanguageSelect={(lang) => { setSelectedLanguage(lang); setCurrentView('editor') }}
          onLogout={handleLogout} />
      ) : (
        <EditorView language={selectedLanguage} user={user}
          onBack={() => { setCurrentView('welcome'); setSelectedLanguage(null) }}
          onLogout={handleLogout} />
      )}
    </div>
  )
}


function WelcomeScreen({ user, onLanguageSelect, onLogout }) {
  const languages = [
    { id: 'python', name: 'Python', ext: '.py', color: '#3572A5' },
    { id: 'nodejs', name: 'Node.js', ext: '.js', color: '#f1e05a' },
    { id: 'java', name: 'Java', ext: '.java', color: '#b07219' },
    { id: 'cpp', name: 'C++', ext: '.cpp', color: '#f34b7d' },
    { id: 'html', name: 'HTML', ext: '.html', color: '#e34c26' },
    { id: 'ubuntu', name: 'Ubuntu Shell', ext: '.sh', color: '#E95420' },
  ]

  return (
    <div className="flex-1 flex flex-col bg-[#1e1e1e]">
      <div className="h-9 bg-[#323233] flex items-center justify-between px-4 text-xs text-[#969696] select-none">
        <span>CloudRun IDE</span>
        <UserBadge user={user} onLogout={onLogout} />
      </div>
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-lg">
          <h1 className="text-4xl font-light mb-2 text-[#cccccc] tracking-tight">CloudRun IDE</h1>
          <p className="text-sm text-[#858585] mb-10">
            {user ? `Welcome back, ${user.display_name || user.username}` : 'Select a language to start coding'}
          </p>
          <div className="space-y-1">
            {languages.map((lang) => (
              <button key={lang.id} onClick={() => onLanguageSelect(lang.id)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded text-left transition-colors hover:bg-[#2a2d2e] group">
                <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: lang.color }} />
                <span className="text-sm text-[#cccccc] group-hover:text-white">{lang.name}</span>
                <span className="text-xs text-[#585858] ml-auto">{lang.ext}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}


function UserBadge({ user, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false)

  if (!user) {
    return <span className="text-[#585858]">Guest</span>
  }

  return (
    <div className="relative">
      <button onClick={() => setMenuOpen(!menuOpen)}
        className="flex items-center gap-2 text-[#969696] hover:text-white transition-colors">
        <span className="w-5 h-5 rounded-full bg-[#0e639c] flex items-center justify-center text-[10px] text-white font-bold uppercase">
          {(user.display_name || user.username || '?')[0]}
        </span>
        <span>{user.display_name || user.username}</span>
        <svg width="10" height="10" viewBox="0 0 16 16" fill="currentColor"><path d="M8 10.5l-4-4h8l-4 4z"/></svg>
      </button>

      {menuOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
          <div className="absolute right-0 top-7 bg-[#3c3c3c] border border-[#555] rounded shadow-xl z-50 w-44 py-1">
            <div className="px-3 py-2 border-b border-[#555]">
              <div className="text-xs text-white font-medium">{user.display_name || user.username}</div>
              <div className="text-[10px] text-[#858585]">{user.email}</div>
            </div>
            <button onClick={() => { setMenuOpen(false); onLogout() }}
              className="w-full text-left px-3 py-1.5 text-xs text-[#cccccc] hover:bg-[#094771] transition-colors">
              Sign Out
            </button>
          </div>
        </>
      )}
    </div>
  )
}


function EditorView({ language, user, onBack, onLogout }) {
  const [code, setCode] = useState(LANGUAGE_CONFIGS[language]?.template || '')
  const [stdin, setStdin] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [lastError, setLastError] = useState(null)
  const [executionTime, setExecutionTime] = useState(null)
  const [bottomTab, setBottomTab] = useState('terminal')
  const [bottomPanelHeight, setBottomPanelHeight] = useState(280)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [isInstalling, setIsInstalling] = useState(false)
  const containerRef = useRef(null)

  const { output, isRunning, executeCode, stopExecution, clearOutput } = useWebSocket()
  const linesOfCode = code.split('\n').length

  useKeyboardShortcuts({
    onRun: handleRunCode, onStop: stopExecution, onClear: clearOutput,
    onSave: () => { try { localStorage.setItem(`code-${language}`, code) } catch {} },
    isRunning,
  })

  useEffect(() => {
    try { const saved = localStorage.getItem(`code-${language}`); if (saved) setCode(saved) } catch {}
  }, [language])

  useEffect(() => {
    if (!output.length) return
    const last = output[output.length - 1]
    if (!last) return
    if (last.type === 'stderr' || last.type === 'error') setLastError(last.content)
    if (last.type === 'complete' && last.content?.includes('failed')) {
      const err = output.filter(m => m.type === 'stdout' || m.type === 'stderr' || m.type === 'error')
        .map(m => m.content).join('\n').trim()
      if (err) setLastError(err)
    }
    if (last.type === 'complete' || last.type === 'error') setIsInstalling(false)
  }, [output])

  const handleMouseDown = useCallback((e) => { e.preventDefault(); setIsDragging(true) }, [])

  useEffect(() => {
    if (!isDragging) return
    const onMove = (e) => {
      if (!containerRef.current) return
      const rect = containerRef.current.getBoundingClientRect()
      setBottomPanelHeight(Math.max(120, Math.min(rect.bottom - e.clientY, rect.height - 200)))
    }
    const onUp = () => setIsDragging(false)
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
    return () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  }, [isDragging])

  const handleFileUpload = async (files) => {
    const newFiles = []
    for (const file of files) {
      if (file.size > 10 * 1024 * 1024) { alert(`File ${file.name} too large`); continue }
      const content = await new Promise((res, rej) => {
        const r = new FileReader(); r.onload = (e) => res(e.target.result); r.onerror = rej; r.readAsText(file)
      })
      newFiles.push({ name: file.name, content, size: file.size })
    }
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  async function handleRunCode() {
    if (isRunning) return
    setLastError(null); setIsInstalling(false)
    const start = Date.now()
    const filesToSend = uploadedFiles.filter(f => f.name !== selectedFile).map(f => ({ name: f.name, content: f.content }))
    await executeCode(language, code, stdin, filesToSend)
    setExecutionTime(Date.now() - start)
  }

  async function handleInstallAndRerun(packages) {
    if (isRunning) return
    setLastError(null); setIsInstalling(true); setBottomTab('terminal')
    const start = Date.now()
    const filesToSend = uploadedFiles.filter(f => f.name !== selectedFile).map(f => ({ name: f.name, content: f.content }))
    await executeCode(language, code, stdin, filesToSend, packages)
    setExecutionTime(Date.now() - start)
  }

  const langNames = { python: 'Python', nodejs: 'JavaScript', java: 'Java', cpp: 'C++', html: 'HTML', ubuntu: 'Ubuntu Shell' }
  const langExts = { python: 'main.py', nodejs: 'index.js', java: 'Main.java', cpp: 'main.cpp', html: 'index.html', ubuntu: 'script.sh' }
  const hasDep = output.some(m => m.type === 'dependency')

  return (
    <div className="flex-1 flex flex-col overflow-hidden" ref={containerRef}>
      {/* Title Bar */}
      <div className="h-9 bg-[#323233] flex items-center justify-between px-3 select-none flex-shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="text-xs text-[#969696] hover:text-white transition-colors flex items-center gap-1">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M7.78 12.53a.75.75 0 01-1.06 0L3.22 9.03a.75.75 0 010-1.06l3.5-3.5a.75.75 0 011.06 1.06L5.56 7.75H12a.75.75 0 010 1.5H5.56l2.22 2.22a.75.75 0 010 1.06z"/></svg>
            Back
          </button>
          <span className="text-xs text-[#969696]">{langNames[language]}</span>
        </div>
        <div className="flex items-center gap-3">
          <UserBadge user={user} onLogout={onLogout} />
          <div className="w-px h-4 bg-[#555]" />
          {isRunning && (
            <button onClick={stopExecution} className="px-2 py-0.5 text-xs bg-[#c53434] hover:bg-[#d04040] text-white rounded transition-colors">Stop</button>
          )}
          <button onClick={handleRunCode} disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-0.5 text-xs rounded transition-colors ${isRunning ? 'bg-[#3a3a3a] text-[#585858] cursor-not-allowed' : 'bg-[#0e639c] hover:bg-[#1177bb] text-white'}`}>
            <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor"><path d="M4.5 3v10l8-5z"/></svg>
            {isRunning ? (isInstalling ? 'Installing...' : 'Running...') : 'Run'}
          </button>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="h-[35px] bg-[#252526] flex items-end border-b border-[#1e1e1e] flex-shrink-0">
        <div className="flex items-center h-[35px] bg-[#1e1e1e] border-r border-[#252526] px-3 text-xs text-[#cccccc]">
          <span className="mr-2 opacity-60 text-[10px]">
            {language === 'ubuntu' ? '$' : language === 'python' ? 'py' : language === 'nodejs' ? 'js' : language === 'java' ? 'java' : language === 'cpp' ? 'cpp' : 'html'}
          </span>
          {selectedFile || langExts[language]}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex flex-1 overflow-hidden">
          {sidebarOpen && (
            <div className="w-64 bg-[#252526] border-r border-[#1e1e1e] flex flex-col flex-shrink-0">
              <div className="px-3 py-2 text-[11px] font-semibold text-[#bbbbbb] uppercase tracking-wider">Explorer</div>
              <div className="flex-1 overflow-y-auto">
                <FileExplorer files={uploadedFiles} selectedFile={selectedFile}
                  onFileSelect={(f) => { setSelectedFile(f.name); setCode(f.content) }}
                  onFileDelete={(f) => { setUploadedFiles(prev => prev.filter(x => x.name !== f.name)); if (selectedFile === f.name) { setSelectedFile(null); setCode(LANGUAGE_CONFIGS[language]?.template || '') } }}
                  onFileUpload={handleFileUpload} />
              </div>
            </div>
          )}
          <div className="flex flex-1 overflow-hidden">
            <div className="w-12 bg-[#333333] flex flex-col items-center py-1 flex-shrink-0">
              <button onClick={() => setSidebarOpen(!sidebarOpen)}
                className={`w-12 h-12 flex items-center justify-center transition-colors ${sidebarOpen ? 'text-white border-l-2 border-white' : 'text-[#858585] hover:text-white'}`}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 7h18M3 12h18M3 17h18"/></svg>
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <CodeEditor language={language} code={code} onChange={setCode} theme="vs-dark" />
            </div>
          </div>
        </div>

        <div onMouseDown={handleMouseDown}
          className={`h-1 cursor-row-resize flex-shrink-0 transition-colors ${isDragging ? 'bg-[#0e639c]' : 'bg-[#414141] hover:bg-[#0e639c]'}`} />

        <div className="flex flex-col flex-shrink-0 bg-[#1e1e1e]" style={{ height: bottomPanelHeight }}>
          <div className="h-[35px] bg-[#252526] flex items-center px-2 gap-0 flex-shrink-0 border-b border-[#1e1e1e]">
            {[
              { id: 'terminal', label: 'Terminal', badge: hasDep },
              { id: 'ai', label: 'AI Assistant', badge: !!lastError },
              { id: 'input', label: 'Input' },
            ].map(tab => (
              <button key={tab.id} onClick={() => setBottomTab(tab.id)}
                className={`px-3 h-full text-xs uppercase tracking-wide transition-colors border-b-2 ${
                  bottomTab === tab.id ? 'text-white border-[#0e639c]' : 'text-[#969696] border-transparent hover:text-[#cccccc]'
                }`}>
                {tab.label} {tab.badge ? <span className="text-[#f44747] ml-1">●</span> : null}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-hidden">
            {bottomTab === 'terminal' && (
              <Console output={output} isRunning={isRunning} onClear={clearOutput}
                onInstallAndRerun={handleInstallAndRerun} isInstalling={isInstalling} />
            )}
            {bottomTab === 'ai' && <AIAssistant code={code} error={lastError} language={language} onCodeUpdate={setCode} />}
            {bottomTab === 'input' && <div className="p-3 h-full"><InputPanel onInputChange={setStdin} disabled={isRunning} /></div>}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-[22px] bg-[#007acc] flex items-center justify-between px-3 text-[11px] text-white flex-shrink-0 select-none">
        <div className="flex items-center gap-3">
          <span>{langNames[language]}</span>
          {isRunning && <span className="flex items-center gap-1"><span className="animate-pulse">●</span> {isInstalling ? 'Installing...' : 'Running'}</span>}
        </div>
        <div className="flex items-center gap-3">
          {user && <span>{user.username}</span>}
          <span>Ln {linesOfCode}</span>
          {executionTime && <span>{(executionTime / 1000).toFixed(1)}s</span>}
          <span>UTF-8</span>
        </div>
      </div>
    </div>
  )
}

export default App
