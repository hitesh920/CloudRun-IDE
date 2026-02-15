/**
 * Auth service — login, register, token management.
 */

const API_BASE = '/api/auth'

class AuthService {
  constructor() {
    this._token = localStorage.getItem('cloudrun_token') || null
    this._user = null
    try {
      const cached = localStorage.getItem('cloudrun_user')
      if (cached) this._user = JSON.parse(cached)
    } catch {}
  }

  get token() { return this._token }
  get user() { return this._user }
  get isLoggedIn() { return !!this._token }

  _setAuth(token, user) {
    this._token = token
    this._user = user
    localStorage.setItem('cloudrun_token', token)
    localStorage.setItem('cloudrun_user', JSON.stringify(user))
  }

  _clearAuth() {
    this._token = null
    this._user = null
    localStorage.removeItem('cloudrun_token')
    localStorage.removeItem('cloudrun_user')
  }

  async _request(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Request failed')
    return data
  }

  async register(username, email, password, displayName = '') {
    const data = await this._request('/register', {
      username, email, password,
      display_name: displayName || username,
    })
    this._setAuth(data.token, data.user)
    return data.user
  }

  async login(username, password) {
    const data = await this._request('/login', { username, password })
    this._setAuth(data.token, data.user)
    return data.user
  }

  logout() {
    this._clearAuth()
  }

  async verify() {
    if (!this._token) return false
    try {
      const res = await fetch(`${API_BASE}/verify`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${this._token}` },
      })
      if (!res.ok) { this._clearAuth(); return false }
      const data = await res.json()
      this._user = data.user
      localStorage.setItem('cloudrun_user', JSON.stringify(data.user))
      return true
    } catch {
      this._clearAuth()
      return false
    }
  }

  async getProfile() {
    if (!this._token) throw new Error('Not authenticated')
    const res = await fetch(`${API_BASE}/me`, {
      headers: { Authorization: `Bearer ${this._token}` },
    })
    if (!res.ok) {
      if (res.status === 401) this._clearAuth()
      throw new Error('Failed to fetch profile')
    }
    const user = await res.json()
    this._user = user
    return user
  }
}

export default new AuthService()
