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
    }
  }, [])

  // Subscribe to WebSocket messages
  useEffect(() => {
    unsubscribeRef.current = websocketService.onMessage(handleMessage)

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current()
      }
    }
  }, [handleMessage])

  // Execute code via WebSocket
  const executeCode = useCallback(async (language, code, stdin = '', files = []) => {
    try {
      // Clear previous output
      setOutput([])
      setIsRunning(true)

      // Connect and execute
      await websocketService.connect(language, code, stdin, files)
      setIsConnected(true)
    } catch (error) {
      setOutput([{
        type: 'error',
        content: `Failed to connect: ${error.message}`,
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

  // Disconnect on unmount
  useEffect(() => {
    return () => {
      websocketService.disconnect()
    }
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
