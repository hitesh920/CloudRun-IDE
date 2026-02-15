import { useState } from 'react'
import authService from '../services/auth'

function AuthScreen({ onAuthSuccess, onSkip }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let user
      if (mode === 'register') {
        user = await authService.register(username, email, password, displayName)
      } else {
        user = await authService.login(username, password)
      }
      onAuthSuccess(user)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-[#1e1e1e]">
      <div className="h-9 bg-[#323233] flex items-center px-4 text-xs text-[#969696] select-none">
        CloudRun IDE
      </div>

      <div className="flex-1 flex items-center justify-center">
        <div className="w-full max-w-sm">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-light text-[#cccccc] tracking-tight mb-1">CloudRun IDE</h1>
            <p className="text-sm text-[#858585]">
              {mode === 'login' ? 'Sign in to your account' : 'Create a new account'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] text-[#969696] uppercase tracking-wider mb-1.5">
                {mode === 'login' ? 'Username or Email' : 'Username'}
              </label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                placeholder={mode === 'login' ? 'username or email' : 'username'}
                required autoFocus
                className="w-full px-3 py-2 bg-[#3c3c3c] border border-[#555] rounded text-sm text-[#cccccc] placeholder-[#666] focus:outline-none focus:border-[#0e639c] transition-colors" />
            </div>

            {mode === 'register' && (
              <div>
                <label className="block text-[11px] text-[#969696] uppercase tracking-wider mb-1.5">Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com" required
                  className="w-full px-3 py-2 bg-[#3c3c3c] border border-[#555] rounded text-sm text-[#cccccc] placeholder-[#666] focus:outline-none focus:border-[#0e639c] transition-colors" />
              </div>
            )}

            {mode === 'register' && (
              <div>
                <label className="block text-[11px] text-[#969696] uppercase tracking-wider mb-1.5">Display Name</label>
                <input type="text" value={displayName} onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Your name (optional)"
                  className="w-full px-3 py-2 bg-[#3c3c3c] border border-[#555] rounded text-sm text-[#cccccc] placeholder-[#666] focus:outline-none focus:border-[#0e639c] transition-colors" />
              </div>
            )}

            <div>
              <label className="block text-[11px] text-[#969696] uppercase tracking-wider mb-1.5">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" required minLength={6}
                className="w-full px-3 py-2 bg-[#3c3c3c] border border-[#555] rounded text-sm text-[#cccccc] placeholder-[#666] focus:outline-none focus:border-[#0e639c] transition-colors" />
            </div>

            {error && (
              <div className="text-xs text-[#f44747] bg-[#3a1d1d] border border-[#5a2d2d] rounded px-3 py-2">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading}
              className={`w-full py-2 rounded text-sm font-medium transition-colors ${loading ? 'bg-[#3a3a3a] text-[#585858] cursor-not-allowed' : 'bg-[#0e639c] hover:bg-[#1177bb] text-white'}`}>
              {loading
                ? (mode === 'login' ? 'Signing in...' : 'Creating account...')
                : (mode === 'login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-[#858585]">
            {mode === 'login' ? (
              <>Don't have an account?{' '}
                <button onClick={() => { setMode('register'); setError('') }}
                  className="text-[#569cd6] hover:text-[#7cb3f0] transition-colors">Create one</button>
              </>
            ) : (
              <>Already have an account?{' '}
                <button onClick={() => { setMode('login'); setError('') }}
                  className="text-[#569cd6] hover:text-[#7cb3f0] transition-colors">Sign in</button>
              </>
            )}
          </div>

          <div className="mt-4 text-center">
            <button onClick={onSkip}
              className="text-xs text-[#585858] hover:text-[#858585] transition-colors">
              Continue as guest →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthScreen
