import { Clock, Cpu, HardDrive, Code } from 'lucide-react'

function StatusBar({ language, isRunning, executionTime, linesOfCode }) {
  return (
    <div className="bg-gray-800 border-t border-gray-700 px-4 py-2 flex items-center justify-between text-xs text-gray-400">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1">
          <Code className="w-3 h-3" />
          <span className="capitalize">{language}</span>
        </div>
        
        {linesOfCode > 0 && (
          <div className="flex items-center gap-1">
            <span>{linesOfCode} lines</span>
          </div>
        )}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {executionTime && (
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{executionTime}ms</span>
          </div>
        )}
        
        <div className="flex items-center gap-1">
          {isRunning ? (
            <>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-green-400">Running</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-gray-500 rounded-full" />
              <span>Ready</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default StatusBar
