/**
 * WebSocket service for real-time code execution
 * Connects through Nginx proxy (relative URL)
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.messageHandlers = new Set()
    this.isConnected = false
  }

  /**
   * Get the WebSocket URL based on current page location
   */
  _getWsUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}`
  }

  /**
   * Connect to WebSocket server and execute code
   */
  connect(language, code, stdin = '', files = []) {
    return new Promise((resolve, reject) => {
      try {
        // Always close existing connection first
        this.disconnect()

        const wsUrl = this._getWsUrl()
        console.log(`🔌 Connecting to ${wsUrl}/ws/execute`)

        this.ws = new WebSocket(`${wsUrl}/ws/execute`)

        // Connection timeout
        const connectTimeout = setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            console.error('❌ WebSocket connection timeout')
            this.ws.close()
            reject(new Error('Connection timeout'))
          }
        }, 10000)

        this.ws.onopen = () => {
          clearTimeout(connectTimeout)
          console.log('✅ WebSocket connected')
          this.isConnected = true

          // Send execution request
          const payload = JSON.stringify({
            language,
            code,
            stdin,
            files,
          })
          
          console.log(`📤 Sending execution request: ${language}, ${code.length} chars`)
          this.ws.send(payload)
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data)
            // Notify all handlers
            this.messageHandlers.forEach(handler => {
              try {
                handler(message)
              } catch (e) {
                console.error('Handler error:', e)
              }
            })
          } catch (error) {
            console.error('Failed to parse message:', error)
          }
        }

        this.ws.onerror = (error) => {
          clearTimeout(connectTimeout)
          console.error('❌ WebSocket error:', error)
          this.isConnected = false
          reject(new Error('WebSocket connection failed'))
        }

        this.ws.onclose = (event) => {
          clearTimeout(connectTimeout)
          console.log(`🔌 WebSocket closed (code: ${event.code}, reason: ${event.reason || 'none'})`)
          this.isConnected = false
          this.ws = null
        }
      } catch (error) {
        console.error('Failed to create WebSocket:', error)
        reject(error)
      }
    })
  }

  /**
   * Register a message handler
   * Returns an unsubscribe function
   */
  onMessage(handler) {
    this.messageHandlers.add(handler)
    
    return () => {
      this.messageHandlers.delete(handler)
    }
  }

  /**
   * Send a message to the server
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  /**
   * Disconnect from WebSocket
   * Does NOT clear message handlers (they persist across connections)
   */
  disconnect() {
    if (this.ws) {
      try {
        if (this.ws.readyState === WebSocket.OPEN || 
            this.ws.readyState === WebSocket.CONNECTING) {
          this.ws.close(1000, 'Client disconnect')
        }
      } catch (e) {
        // Ignore close errors
      }
      this.ws = null
      this.isConnected = false
    }
  }

  /**
   * Check if connected
   */
  getConnectionStatus() {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN
  }
}

// Export singleton instance
export default new WebSocketService()
