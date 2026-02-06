/**
 * WebSocket service for real-time code execution
 */

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

class WebSocketService {
  constructor() {
    this.ws = null
    this.messageHandlers = []
    this.isConnected = false
  }

  /**
   * Connect to WebSocket server and execute code
   */
  connect(language, code, stdin = '') {
    return new Promise((resolve, reject) => {
      try {
        // Close existing connection if any
        this.disconnect()

        // Create WebSocket connection
        this.ws = new WebSocket(`${WS_URL}/ws/execute`)

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected')
          this.isConnected = true

          // Send execution request
          this.ws.send(JSON.stringify({
            language,
            code,
            stdin,
          }))

          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            console.log('📨 Received:', message)

            // Call all registered message handlers
            this.messageHandlers.forEach(handler => handler(message))
          } catch (error) {
            console.error('Failed to parse message:', error)
          }
        }

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('👋 WebSocket disconnected')
          this.isConnected = false
        }
      } catch (error) {
        console.error('Failed to connect:', error)
        reject(error)
      }
    })
  }

  /**
   * Register a message handler
   */
  onMessage(handler) {
    this.messageHandlers.push(handler)
    
    // Return unsubscribe function
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
    }
  }

  /**
   * Send a message to the server
   */
  send(message) {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify(message))
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.isConnected = false
      this.messageHandlers = []
    }
  }

  /**
   * Check if connected
   */
  getConnectionStatus() {
    return this.isConnected
  }
}

// Export singleton instance
export default new WebSocketService()
