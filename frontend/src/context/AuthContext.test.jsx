import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { AuthProvider, useAuthContext } from './AuthContext'
import { makeJwt, makeUser, faker } from '../test/helpers'

function wrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

beforeEach(() => {
  localStorage.clear()
  vi.useRealTimers()
})

describe('AuthContext', () => {
  describe('initial state', () => {
    it('should start unauthenticated when no token in localStorage', () => {
      const { result } = renderHook(() => useAuthContext(), { wrapper })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should restore user from valid token in localStorage', () => {
      const payload = makeUser()
      const token = makeJwt(payload)
      localStorage.setItem('duppla_token', token)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      expect(result.current.user).not.toBeNull()
      expect(result.current.user.email).toBe(payload.email)
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('should clear expired token on init', () => {
      const expired = makeJwt({ exp: Math.floor(Date.now() / 1000) - 3600 })
      localStorage.setItem('duppla_token', expired)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      expect(result.current.user).toBeNull()
      expect(localStorage.getItem('duppla_token')).toBeNull()
    })

    it('should treat token with no exp field as expired', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
      const payload = { sub: faker.string.uuid(), email: faker.internet.email(), name: faker.person.fullName(), role: 'admin', status: 'active' }
      const body = btoa(JSON.stringify(payload)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
      const noExpToken = `${header}.${body}.fake-signature`
      localStorage.setItem('duppla_token', noExpToken)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      expect(result.current.user).toBeNull()
      expect(localStorage.getItem('duppla_token')).toBeNull()
    })
  })

  describe('login', () => {
    it('should set user and token from valid JWT', () => {
      const payload = makeUser()
      const token = makeJwt(payload)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login(token)
      })

      expect(result.current.user.email).toBe(payload.email)
      expect(result.current.token).toBe(token)
      expect(result.current.isAuthenticated).toBe(true)
      expect(localStorage.getItem('duppla_token')).toBe(token)
    })

    it('should ignore expired token on login', () => {
      const expired = makeJwt({ exp: Math.floor(Date.now() / 1000) - 60 })

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login(expired)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should ignore malformed token on login', () => {
      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login('not.a.valid.jwt')
      })

      expect(result.current.user).toBeNull()
    })
  })

  describe('logout', () => {
    it('should clear user, token and localStorage', () => {
      const token = makeJwt()
      localStorage.setItem('duppla_token', token)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.logout()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
      expect(localStorage.getItem('duppla_token')).toBeNull()
    })
  })

  describe('computed values', () => {
    it('should set isPending when user status is pending', () => {
      const token = makeJwt({ status: 'pending' })

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login(token)
      })

      expect(result.current.isPending).toBe(true)
      expect(result.current.isActive).toBe(false)
    })

    it('should set isActive when user status is active', () => {
      const token = makeJwt({ status: 'active' })

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login(token)
      })

      expect(result.current.isActive).toBe(true)
      expect(result.current.isPending).toBe(false)
    })
  })

  describe('auto-expire', () => {
    it('should auto-logout when token expires', () => {
      vi.useFakeTimers()
      const expInMs = 5000
      const token = makeJwt({
        exp: Math.floor(Date.now() / 1000) + expInMs / 1000,
      })

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        result.current.login(token)
      })

      expect(result.current.isAuthenticated).toBe(true)

      act(() => {
        vi.advanceTimersByTime(expInMs + 100)
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should logout immediately when restored token has already expired (ms <= 0)', () => {
      vi.useFakeTimers({ now: 1000000000000 })
      const token = makeJwt({ exp: 1000000000 })

      localStorage.setItem('duppla_token', token)

      const { result } = renderHook(() => useAuthContext(), { wrapper })

      act(() => {
        vi.runAllTimers()
      })

      expect(result.current.user).toBeNull()
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('useAuthContext outside provider', () => {
    it('should throw when used without AuthProvider', () => {
      expect(() => {
        renderHook(() => useAuthContext())
      }).toThrow('useAuthContext must be used inside AuthProvider')
    })
  })
})
