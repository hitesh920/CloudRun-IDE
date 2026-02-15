/**
 * REST API service for CloudRun IDE
 * Uses relative URLs to go through Nginx proxy in production
 */

class ApiService {
  constructor() {
    // Use relative URL - works both in dev (via Vite proxy) and prod (via Nginx)
    this.baseURL = ''
  }

  /**
   * Generic fetch wrapper
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    }

    try {
      const response = await fetch(url, { ...defaultOptions, ...options })
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  /**
   * Get API health status
   */
  async healthCheck() {
    return this.request('/health')
  }

  /**
   * Get system status
   */
  async getStatus() {
    return this.request('/api/status')
  }

  /**
   * Get supported languages
   */
  async getLanguages() {
    return this.request('/api/languages')
  }

  /**
   * Get code template for a language
   */
  async getTemplate(language) {
    return this.request(`/api/templates/${language}`)
  }

  /**
   * Get all code templates
   */
  async getAllTemplates() {
    return this.request('/api/templates')
  }

  /**
   * Execute code (synchronous)
   */
  async executeCode(language, code, stdin = '') {
    return this.request('/api/execute', {
      method: 'POST',
      body: JSON.stringify({
        language,
        code,
        stdin,
      }),
    })
  }

  /**
   * Stop an execution
   */
  async stopExecution(executionId) {
    return this.request(`/api/execute/stop/${executionId}`, {
      method: 'POST',
    })
  }

  /**
   * Get AI assistant status
   */
  async getAIStatus() {
    return this.request('/api/ai/status')
  }
}

// Export singleton instance
export default new ApiService()
