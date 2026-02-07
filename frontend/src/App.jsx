import { useState } from 'react'
import { CodeEditor, LANGUAGE_CONFIGS } from './components/Editor'
import Console from './components/Console'
import InputPanel from './components/InputPanel'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const [currentView, setCurrentView] = useState('welcome') // 'welcome' or 'editor'
  const [selectedLanguage, setSelectedLanguage] = useState(null)

  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language)
    setCurrentView('editor')
  }

  const handleBackToWelcome = () => {
    setCurrentView('welcome')
    setSelectedLanguage(null)
  }

  return (
    <div className="h-screen w-screen bg-gray-900 text-white flex flex-col">
      {currentView === 'welcome' ? (
        <WelcomeScreen onLanguageSelect={handleLanguageSelect} />
      ) : (
        <EditorView 
          language={selectedLanguage} 
          onBack={handleBackToWelcome}
        />
      )}
    </div>
  )
}

function WelcomeScreen({ onLanguageSelect }) {
  const languages = [
    { id: 'python', name: 'Python', icon: '🐍' },
    { id: 'nodejs', name: 'Node.js', icon: '🟢' },
    { id: 'java', name: 'Java', icon: '☕' },
    { id: 'cpp', name: 'C++', icon: '⚡' },
    { id: 'html', name: 'HTML/CSS/JS', icon: '🌐' },
  ]

  return (
    <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          CloudRun IDE
        </h1>
        <p className="text-xl text-gray-400 mb-12">
          Choose a programming language to start coding
        </p>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 max-w-4xl">
          {languages.map((lang) => (
            <button
              key={lang.id}
              onClick={() => onLanguageSelect(lang.id)}
              className="bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-blue-500 
                         rounded-lg p-8 transition-all duration-200 transform hover:scale-105
                         hover:shadow-lg hover:shadow-blue-500/20"
            >
              <div className="text-5xl mb-3">{lang.icon}</div>
              <div className="text-lg font-semibold">{lang.name}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function EditorView({ language, onBack }) {
  const [code, setCode] = useState(LANGUAGE_CONFIGS[language]?.template || '')
  const [stdin, setStdin] = useState('')
  const { output, isRunning, executeCode, stopExecution, clearOutput } = useWebSocket()

  const handleRunCode = async () => {
    await executeCode(language, code, stdin)
  }

  const handleStopExecution = () => {
    stopExecution()
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ← Back
          </button>
          <h2 className="text-lg font-semibold capitalize">{language}</h2>
        </div>
        
        <div className="flex items-center gap-2">
          {isRunning && (
            <button 
              onClick={handleStopExecution}
              className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 transition-colors"
            >
              Stop
            </button>
          )}
          <button 
            onClick={handleRunCode}
            disabled={isRunning}
            className={`px-4 py-2 rounded-md transition-colors ${
              isRunning 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>
      </div>

      {/* Editor and Console */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor */}
        <div className="flex-1 p-4 flex flex-col gap-4">
          {/* Input Panel */}
          <InputPanel 
            onInputChange={setStdin}
            disabled={isRunning}
          />
          
          {/* Code Editor */}
          <div className="flex-1">
            <CodeEditor
              language={language}
              code={code}
              onChange={setCode}
            />
          </div>
        </div>
        
        {/* Console */}
        <div className="w-1/3 p-4 border-l border-gray-700">
          <Console 
            output={output}
            isRunning={isRunning}
            onClear={clearOutput}
          />
        </div>
      </div>
    </div>
  )
}

export default App
