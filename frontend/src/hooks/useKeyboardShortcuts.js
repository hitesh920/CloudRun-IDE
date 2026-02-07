/**
 * Custom React hook for keyboard shortcuts
 */

import { useEffect } from 'react'

export function useKeyboardShortcuts({
  onRun,
  onStop,
  onClear,
  onSave,
  isRunning = false,
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl/Cmd + Enter - Run code
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault()
        if (!isRunning && onRun) {
          onRun()
        }
      }

      // Ctrl/Cmd + Shift + S - Stop execution
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
        e.preventDefault()
        if (isRunning && onStop) {
          onStop()
        }
      }

      // Ctrl/Cmd + K - Clear console
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        if (onClear) {
          onClear()
        }
      }

      // Ctrl/Cmd + S - Save (preventDefault to avoid browser save)
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        if (onSave) {
          onSave()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [onRun, onStop, onClear, onSave, isRunning])
}
