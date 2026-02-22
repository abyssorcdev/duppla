const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const authApi = {
  /** Redirects browser to backend Google OAuth flow */
  loginWithGoogle: () => {
    window.location.href = `${API_BASE}/auth/google`
  },
}
