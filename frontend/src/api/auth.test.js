import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('authApi', () => {
  describe('loginWithGoogle', () => {
    let originalLocation

    beforeEach(() => {
      originalLocation = window.location
      delete window.location
      window.location = { href: '' }
    })

    afterEach(() => {
      window.location = originalLocation
      vi.unstubAllEnvs()
      vi.resetModules()
    })

    it('should redirect to backend Google OAuth endpoint', async () => {
      const { authApi } = await import('./auth')
      authApi.loginWithGoogle()
      expect(window.location.href).toContain('/auth/google')
    })

    it('should use VITE_API_URL when set', async () => {
      vi.stubEnv('VITE_API_URL', 'https://custom-api.example.com')
      vi.resetModules()
      const { authApi } = await import('./auth')
      authApi.loginWithGoogle()
      expect(window.location.href).toBe('https://custom-api.example.com/auth/google')
    })
  })
})
