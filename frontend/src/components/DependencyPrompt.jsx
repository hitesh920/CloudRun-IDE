import { AlertCircle, Package, X } from 'lucide-react'

function DependencyPrompt({ 
  packageName, 
  packageManager, 
  installCommand,
  onInstall, 
  onDismiss,
  isInstalling = false 
}) {
  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 border border-yellow-600 rounded-lg shadow-lg p-4 max-w-md z-50">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <AlertCircle className="w-5 h-5 text-yellow-500" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-white mb-1">
            Missing Dependency
          </h3>
          
          <p className="text-sm text-gray-300 mb-3">
            Package <span className="text-yellow-400 font-mono">{packageName}</span> is not installed.
            Would you like to install it?
          </p>
          
          {installCommand && (
            <div className="bg-gray-900 rounded px-3 py-2 mb-3">
              <code className="text-xs text-gray-400 font-mono">
                {installCommand}
              </code>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            <button
              onClick={onInstall}
              disabled={isInstalling}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
                isInstalling
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              <Package className="w-4 h-4" />
              {isInstalling ? 'Installing...' : 'Install'}
            </button>
            
            <button
              onClick={onDismiss}
              disabled={isInstalling}
              className="px-3 py-1.5 rounded text-sm bg-gray-700 hover:bg-gray-600 transition-colors disabled:opacity-50"
            >
              Dismiss
            </button>
          </div>
        </div>
        
        <button
          onClick={onDismiss}
          disabled={isInstalling}
          className="flex-shrink-0 text-gray-500 hover:text-white transition-colors disabled:opacity-50"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

export default DependencyPrompt
