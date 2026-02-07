import { useState, useEffect } from 'react'
import { CodeEditor, LANGUAGE_CONFIGS } from './components/Editor'
import Console from './components/Console'
import InputPanel from './components/InputPanel'
import FileExplorer from './components/FileExplorer'
import DependencyPrompt from './components/DependencyPrompt'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const [currentView, setCurrentView] = useState('welcome')
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
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [missingDependency, setMissingDependency] = useState(null)
  
  const { output, isRunning, executeCode, stopExecution, clearOutput } = useWebSocket()

  // Listen for dependency messages
  useEffect(() => {
    const lastMessage = output[output.length - 1]
    if (lastMessage && lastMessage.type === 'dependency') {
      setMissingDependency({
        packageName: lastMessage.package_name,
        packageManager: lastMessage.package_manager,
        installCommand: lastMessage.install_command,
      })
    }
  }, [output])

  const handleFileUpload = async (files) => {
    const newFiles = []
    
    for (const file of files) {
      if (file.size > 10 * 1024 * 1024) {
        alert(`File ${file.name} is too large (max 10MB)`)
        continue
      }
      
      const content = await readFileContent(file)
      newFiles.push({ name: file.name, content: content, size: file.size })
    }
    
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const handleFileSelect = (file) => {
    setSelectedFile(file.name)
    setCode(file.content)
  }

  const handleFileDelete = (fileToDelete) => {
    setUploadedFiles(prev => prev.filter(f => f.name !== fileToDelete.name))
    if (selectedFile === fileToDelete.name) {
      setSelectedFile(null)
      setCode(LANGUAGE_CONFIGS[language]?.template || '')
    }
  }

  const handleRunCode = async () => {
    setMissingDependency(null)
    
    const filesToSend = uploadedFiles.filter(f => f.name !== selectedFile).map(f => ({
      name: f.name,
      content: f.content,
    }))
    
    await executeCode(language, code, stdin, filesToSend)
  }

  const handleStopExecution = () => {
    stopExecution()
  }

  const handleInstallDependency = async () => {
    alert('Dependency installation coming in next commit!')
    setMissingDependency(null)
  }

  const handleDismissDependency = () => {
    setMissingDependency(null)
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="text-gray-400 hover:text-white transition-colors">
            ← Back
          </button>
          <h2 className="text-lg font-semibold capitalize">{language}</h2>
          {selectedFile && <span className="text-sm text-gray-400">Editing: {selectedFile}</span>}
        </div>
        
        <div className="flex items-center gap-2">
          {isRunning && (
            <button onClick={handleStopExecution} className="px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 transition-colors">
              Stop
            </button>
          )}
          <button 
            onClick={handleRunCode}
            disabled={isRunning}
            className={`px-4 py-2 rounded-md transition-colors ${isRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 p-4 flex flex-col gap-4">
          <FileExplorer
            files={uploadedFiles}
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            onFileDelete={handleFileDelete}
            onFileUpload={handleFileUpload}
          />
          
          <InputPanel onInputChange={setStdin} disabled={isRunning} />
          
          <div className="flex-1">
            <CodeEditor language={language} code={code} onChange={setCode} />
          </div>
        </div>
        
        <div className="w-1/3 p-4 border-l border-gray-700">
          <Console output={output} isRunning={isRunning} onClear={clearOutput} />
        </div>
      </div>

      {missingDependency && (
        <DependencyPrompt
          packageName={missingDependency.packageName}
          packageManager={missingDependency.packageManager}
          installCommand={missingDependency.installCommand}
          onInstall={handleInstallDependency}
          onDismiss={handleDismissDependency}
        />
      )}
    </div>
  )
}

export default App
