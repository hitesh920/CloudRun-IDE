/**
 * Custom React hook for WebSocket code execution
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import websocketService from '../services/websocket'

export function useWebSocket() {
  const [output, setOutput] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const unsubscribeRef = useRef(null)

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message) => {
    setOutput(prev => [...prev, message])

    // Update running state based on message type
    if (message.type === 'status' && message.content.includes('Running')) {
      setIsRunning(true)
    }

    if (message.type === 'complete' || message.type === 'error') {
      setIsRunning(false)
      setIsConnected(false)
    }
  }, [])

  // Subscribe to WebSocket messages on mount
  useEffect(() => {
    // Register handler once - it persists across connections
    unsubscribeRef.current = websocketService.onMessage(handleMessage)

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current()
        unsubscribeRef.current = null
      }
      websocketService.disconnect()
    }
  }, [handleMessage])

  // Execute code via WebSocket
  const executeCode = useCallback(async (language, code, stdin = '', files = []) => {
    try {
      // Clear previous output
      setOutput([])
      setIsRunning(true)
      setIsConnected(false)

      // Connect and execute (disconnect happens automatically in websocket service)
      await websocketService.connect(language, code, stdin, files)
      setIsConnected(true)
    } catch (error) {
      console.error('Execute error:', error)
      setOutput(prev => [...prev, {
        type: 'error',
        content: `Connection failed: ${error.message}. Make sure the backend is running.`,
        timestamp: new Date().toISOString(),
      }])
      setIsRunning(false)
      setIsConnected(false)
    }
  }, [])

  // Stop execution
  const stopExecution = useCallback(() => {
    websocketService.disconnect()
    setIsRunning(false)
    setIsConnected(false)
    setOutput(prev => [...prev, {
      type: 'status',
      content: 'Execution stopped by user',
      timestamp: new Date().toISOString(),
    }])
  }, [])

  // Clear output
  const clearOutput = useCallback(() => {
    setOutput([])
  }, [])

  return {
    output,
    isRunning,
    isConnected,
    executeCode,
    stopExecution,
    clearOutput,
  }
}
