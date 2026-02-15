import { useState, useEffect, useRef } from 'react'
import { CodeEditor, LANGUAGE_CONFIGS } from './components/Editor'
import Console from './components/Console'
import InputPanel from './components/InputPanel'
import FileExplorer from './components/FileExplorer'
import DependencyPrompt from './components/DependencyPrompt'
import AIAssistant from './components/AIAssistant'
import { useWebSocket } from './hooks/useWebSocket'
import { useTheme } from './hooks/useTheme'
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts'

function App() {
  const [currentView, setCurrentView] = useState('welcome')
  const [selectedLanguage, setSelectedLanguage] = useState(null)
  const { theme, toggleTheme } = useTheme()

  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language)
    setCurrentView('editor')
  }

  const handleBackToWelcome = () => {
    setCurrentView('welcome')
    setSelectedLanguage(null)
  }

  return (
    <div className="h-screen w-screen flex flex-col bg-[#1e1e1e] text-[#cccccc]">
      {currentView === 'welcome' ? (
        <WelcomeScreen onLanguageSelect={handleLanguageSelect} />
      ) : (
        <EditorView 
          language={selectedLanguage} 
          onBack={handleBackToWelcome}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      )}
    </div>
  )
}

function WelcomeScreen({ onLanguageSelect }) {
  const languages = [
    { id: 'python', name: 'Python', ext: '.py', color: '#3572A5' },
    { id: 'nodejs', name: 'Node.js', ext: '.js', color: '#f1e05a' },
    { id: 'java', name: 'Java', ext: '.java', color: '#b07219' },
    { id: 'cpp', name: 'C++', ext: '.cpp', color: '#f34b7d' },
    { id: 'html', name: 'HTML', ext: '.html', color: '#e34c26' },
  ]

  return (
    <div className="flex-1 flex flex-col bg-[#1e1e1e]">
      <div className="h-9 bg-[#323233] flex items-center px-4 text-xs text-[#969696] select-none">
        CloudRun IDE
      </div>
      
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-lg">
          <h1 className="text-4xl font-light mb-2 text-[#cccccc] tracking-tight">
            CloudRun IDE
          </h1>
          <p className="text-sm text-[#858585] mb-10">
            Start by selecting a language
          </p>
          
          <div className="space-y-1">
            {languages.map((lang) => (
              <button
                key={lang.id}
                onClick={() => onLanguageSelect(lang.id)}
                className="w-full flex items-center gap-3 px-4 py-3 rounded text-left transition-colors hover:bg-[#2a2d2e] group"
              >
                <span 
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: lang.color }}
                />
                <span className="text-sm text-[#cccccc] group-hover:text-white">
                  {lang.name}
                </span>
                <span className="text-xs text-[#585858] ml-auto">
                  {lang.ext}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function EditorView({ language, onBack, theme, onToggleTheme }) {
  const [code, setCode] = useState(LANGUAGE_CONFIGS[language]?.template || '')
  const [stdin, setStdin] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [missingDependency, setMissingDependency] = useState(null)
  const [lastError, setLastError] = useState(null)
  const [executionTime, setExecutionTime] = useState(null)
  const [bottomTab, setBottomTab] = useState('terminal')
  const [bottomPanelHeight, setBottomPanelHeight] = useState(280)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const outputRef = useRef([])
  
  const { output, isRunning, executeCode, stopExecution, clearOutput } = useWebSocket()

  const linesOfCode = code.split('\n').length

  useKeyboardShortcuts({
    onRun: handleRunCode,
    onStop: stopExecution,
    onClear: clearOutput,
    onSave: () => {
      try { localStorage.setItem(`code-${language}`, code) } catch {}
    },
    isRunning,
  })

  useEffect(() => {
    try {
      const saved = localStorage.getItem(`code-${language}`)
      if (saved) setCode(saved)
    } catch {}
  }, [language])

  // Track errors properly - capture ALL output when execution fails
  useEffect(() => {
    if (!output.length) return
    const lastMessage = output[output.length - 1]
    
    if (lastMessage) {
      if (lastMessage.type === 'dependency') {
        setMissingDependency({
          packageName: lastMessage.package_name,
          packageManager: lastMessage.package_manager,
          installCommand: lastMessage.install_command,
        })
      }
      
      // Track stderr/error messages
      if (lastMessage.type === 'stderr' || lastMessage.type === 'error') {
        setLastError(lastMessage.content)
      }
      
      // When execution completes with failure, collect ALL stdout as error too
      if (lastMessage.type === 'complete' && lastMessage.content?.includes('failed')) {
        const errorLines = output
          .filter(m => m.type === 'stdout' || m.type === 'stderr' || m.type === 'error')
          .map(m => m.content)
          .join('\n')
          .trim()
        if (errorLines) {
          setLastError(errorLines)
        }
      }
    }
  }, [output])

  const handleFileUpload = async (files) => {
    const newFiles = []
    for (const file of files) {
      if (file.size > 10 * 1024 * 1024) { alert(`File ${file.name} too large`); continue }
      const content = await readFileContent(file)
      newFiles.push({ name: file.name, content, size: file.size })
    }
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const readFileContent = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = reject
    reader.readAsText(file)
  })

  const handleFileSelect = (file) => { setSelectedFile(file.name); setCode(file.content) }
  const handleFileDelete = (f) => {
    setUploadedFiles(prev => prev.filter(x => x.name !== f.name))
    if (selectedFile === f.name) { setSelectedFile(null); setCode(LANGUAGE_CONFIGS[language]?.template || '') }
  }

  async function handleRunCode() {
    if (isRunning) return
    setMissingDependency(null)
    setLastError(null)
    const startTime = Date.now()
    const filesToSend = uploadedFiles.filter(f => f.name !== selectedFile).map(f => ({ name: f.name, content: f.content }))
    await executeCode(language, code, stdin, filesToSend)
    setExecutionTime(Date.now() - startTime)
  }

  const langNames = { python: 'Python', nodejs: 'JavaScript', java: 'Java', cpp: 'C++', html: 'HTML' }
  const langExts = { python: 'main.py', nodejs: 'index.js', java: 'Main.java', cpp: 'main.cpp', html: 'index.html' }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Title Bar */}
      <div className="h-9 bg-[#323233] flex items-center justify-between px-3 select-none flex-shrink-0" style={{ WebkitAppRegion: 'drag' }}>
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="text-xs text-[#969696] hover:text-white transition-colors flex items-center gap-1" style={{ WebkitAppRegion: 'no-drag' }}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor"><path d="M7.78 12.53a.75.75 0 01-1.06 0L3.22 9.03a.75.75 0 010-1.06l3.5-3.5a.75.75 0 011.06 1.06L5.56 7.75H12a.75.75 0 010 1.5H5.56l2.22 2.22a.75.75 0 010 1.06z"/></svg>
            Back
          </button>
          <span className="text-xs text-[#969696]">
            {langNames[language] || language}
          </span>
        </div>
        
        <div className="flex items-center gap-2" style={{ WebkitAppRegion: 'no-drag' }}>
          {isRunning && (
            <button onClick={stopExecution} className="px-2 py-0.5 text-xs bg-[#c53434] hover:bg-[#d04040] text-white rounded transition-colors">
              Stop
            </button>
          )}
          <button 
            onClick={handleRunCode}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-0.5 text-xs rounded transition-colors ${
              isRunning 
                ? 'bg-[#3a3a3a] text-[#585858] cursor-not-allowed' 
                : 'bg-[#0e639c] hover:bg-[#1177bb] text-white'
            }`}
          >
            <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
              <path d="M4.5 3v10l8-5z"/>
            </svg>
            {isRunning ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>

      {/* Tab Bar */}
      <div className="h-[35px] bg-[#252526] flex items-end border-b border-[#1e1e1e] flex-shrink-0">
        <div className="flex items-center h-[35px] bg-[#1e1e1e] border-r border-[#252526] px-3 text-xs text-[#cccccc]">
          <span className="mr-2 opacity-60">
            {language === 'python' ? '🐍' : language === 'nodejs' ? 'JS' : language === 'java' ? '☕' : language === 'cpp' ? '⚡' : '🌐'}
          </span>
          {selectedFile || langExts[language] || 'untitled'}
        </div>
      </div>

      {/* Main Content: Editor + Bottom Panel */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar (collapsible) */}
          {sidebarOpen && (
            <div className="w-64 bg-[#252526] border-r border-[#1e1e1e] flex flex-col flex-shrink-0">
              <div className="px-3 py-2 text-[11px] font-semibold text-[#bbbbbb] uppercase tracking-wider">
                Explorer
              </div>
              <div className="flex-1 overflow-y-auto">
                <FileExplorer
                  files={uploadedFiles}
                  selectedFile={selectedFile}
                  onFileSelect={handleFileSelect}
                  onFileDelete={handleFileDelete}
                  onFileUpload={handleFileUpload}
                />
              </div>
            </div>
          )}

          {/* Activity Bar + Editor */}
          <div className="flex flex-1 overflow-hidden">
            {/* Activity Bar */}
            <div className="w-12 bg-[#333333] flex flex-col items-center py-1 flex-shrink-0">
              <button 
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={`w-12 h-12 flex items-center justify-center transition-colors ${sidebarOpen ? 'text-white border-l-2 border-white' : 'text-[#858585] hover:text-white'}`}
                title="Explorer"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M3 7h18M3 12h18M3 17h18"/>
                </svg>
              </button>
            </div>

            {/* Editor Area */}
            <div className="flex-1 overflow-hidden">
              <CodeEditor 
                language={language} 
                code={code} 
                onChange={setCode} 
                theme="vs-dark"
              />
            </div>
          </div>
        </div>

        {/* Resizable Bottom Panel */}
        <div 
          className="flex flex-col flex-shrink-0 bg-[#1e1e1e] border-t border-[#414141]"
          style={{ height: bottomPanelHeight }}
        >
          {/* Panel Tabs */}
          <div className="h-[35px] bg-[#252526] flex items-center px-2 gap-0 flex-shrink-0 border-b border-[#1e1e1e]">
            <button
              onClick={() => setBottomTab('terminal')}
              className={`px-3 h-full text-xs uppercase tracking-wide transition-colors border-b-2 ${
                bottomTab === 'terminal'
                  ? 'text-white border-[#0e639c]'
                  : 'text-[#969696] border-transparent hover:text-[#cccccc]'
              }`}
            >
              Terminal
            </button>
            <button
              onClick={() => setBottomTab('ai')}
              className={`px-3 h-full text-xs uppercase tracking-wide transition-colors border-b-2 ${
                bottomTab === 'ai'
                  ? 'text-white border-[#0e639c]'
                  : 'text-[#969696] border-transparent hover:text-[#cccccc]'
              }`}
            >
              AI Assistant {lastError ? '●' : ''}
            </button>
            <button
              onClick={() => setBottomTab('input')}
              className={`px-3 h-full text-xs uppercase tracking-wide transition-colors border-b-2 ${
                bottomTab === 'input'
                  ? 'text-white border-[#0e639c]'
                  : 'text-[#969696] border-transparent hover:text-[#cccccc]'
              }`}
            >
              Input
            </button>
          </div>

          {/* Panel Content */}
          <div className="flex-1 overflow-hidden">
            {bottomTab === 'terminal' && (
              <Console output={output} isRunning={isRunning} onClear={clearOutput} />
            )}
            {bottomTab === 'ai' && (
              <AIAssistant code={code} error={lastError} language={language} />
            )}
            {bottomTab === 'input' && (
              <div className="p-3 h-full">
                <InputPanel onInputChange={setStdin} disabled={isRunning} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-[22px] bg-[#007acc] flex items-center justify-between px-3 text-[11px] text-white flex-shrink-0 select-none">
        <div className="flex items-center gap-3">
          <span>{langNames[language] || language}</span>
          {isRunning && <span className="flex items-center gap-1"><span className="animate-pulse">●</span> Running</span>}
        </div>
        <div className="flex items-center gap-3">
          <span>Ln {linesOfCode}</span>
          {executionTime && <span>{(executionTime / 1000).toFixed(1)}s</span>}
          <span>UTF-8</span>
        </div>
      </div>

      {missingDependency && (
        <DependencyPrompt
          packageName={missingDependency.packageName}
          packageManager={missingDependency.packageManager}
          installCommand={missingDependency.installCommand}
          onInstall={() => { alert('Coming soon!'); setMissingDependency(null) }}
          onDismiss={() => setMissingDependency(null)}
        />
      )}
    </div>
  )
}

export default App
