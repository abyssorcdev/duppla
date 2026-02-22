import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const TOKEN_KEY = 'duppla_token'

/**
 * Decode the payload of a JWT without verifying signature.
 * Verification happens server-side on every request.
 */
function decodeToken(token) {
  try {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
  } catch {
    return null
  }
}

function isExpired(decoded) {
  if (!decoded?.exp) return true
  return decoded.exp * 1000 < Date.now()
}

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(TOKEN_KEY)
    if (!stored) return null
    const decoded = decodeToken(stored)
    if (!decoded || isExpired(decoded)) {
      localStorage.removeItem(TOKEN_KEY)
      return null
    }
    return decoded
  })

  const login = useCallback((newToken) => {
    const decoded = decodeToken(newToken)
    if (!decoded || isExpired(decoded)) return
    localStorage.setItem(TOKEN_KEY, newToken)
    setToken(newToken)
    setUser(decoded)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  // Proactively clear state if token expires while app is open
  useEffect(() => {
    if (!user?.exp) return
    const ms = user.exp * 1000 - Date.now()
    if (ms <= 0) { logout(); return }
    const timer = setTimeout(logout, ms)
    return () => clearTimeout(timer)
  }, [user, logout])

  const value = useMemo(() => ({
    token,
    user,
    isAuthenticated: !!user && !isExpired(user),
    isPending: user?.status === 'pending',
    isActive: user?.status === 'active',
    login,
    logout,
  }), [token, user, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthContext() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuthContext must be used inside AuthProvider')
  return ctx
}
