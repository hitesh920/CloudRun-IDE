import { useState } from 'react'
import { File, Folder, X, Upload, Plus } from 'lucide-react'

function FileExplorer({ files = [], onFileSelect, onFileDelete, onFileUpload, selectedFile }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    if (droppedFiles.length > 0 && onFileUpload) {
      onFileUpload(droppedFiles)
    }
  }

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files)
    if (selectedFiles.length > 0 && onFileUpload) {
      onFileUpload(selectedFiles)
    }
  }

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase()
    const iconClass = "w-4 h-4"
    
    switch (ext) {
      case 'py':
        return <File className={`${iconClass} text-blue-400`} />
      case 'js':
      case 'jsx':
        return <File className={`${iconClass} text-yellow-400`} />
      case 'java':
        return <File className={`${iconClass} text-red-400`} />
      case 'cpp':
      case 'c':
      case 'h':
        return <File className={`${iconClass} text-purple-400`} />
      case 'html':
        return <File className={`${iconClass} text-orange-400`} />
      case 'css':
        return <File className={`${iconClass} text-blue-300`} />
      default:
        return <File className={`${iconClass} text-gray-400`} />
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
          <Folder className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">Files</span>
          {files.length > 0 && (
            <span className="text-xs text-gray-500">({files.length})</span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <label 
            className="cursor-pointer text-gray-400 hover:text-white transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
            />
            <Upload className="w-4 h-4" />
          </label>
          <span className="text-gray-500 text-sm">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* File List */}
      {isExpanded && (
        <div 
          className={`p-2 min-h-[100px] transition-colors ${
            isDragging ? 'bg-blue-900/20 border-2 border-dashed border-blue-500' : ''
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {files.length === 0 ? (
            <div className="text-center py-6 text-gray-500 text-sm">
              <Upload className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No files uploaded</p>
              <p className="text-xs mt-1">Drag & drop or click upload</p>
            </div>
          ) : (
            <div className="space-y-1">
              {files.map((file, index) => (
                <div
                  key={index}
                  onClick={() => onFileSelect && onFileSelect(file)}
                  className={`flex items-center justify-between px-3 py-2 rounded cursor-pointer transition-colors ${
                    selectedFile === file.name
                      ? 'bg-blue-600/20 border border-blue-500'
                      : 'hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {getFileIcon(file.name)}
                    <span className="text-sm text-gray-200 truncate">
                      {file.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </span>
                  </div>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onFileDelete && onFileDelete(file)
                    }}
                    className="text-gray-500 hover:text-red-400 transition-colors ml-2"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

export default FileExplorer
