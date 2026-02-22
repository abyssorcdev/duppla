import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { faker } from '../test/helpers'

const mockContext = {
  user: null,
  token: null,
  isAuthenticated: false,
  isPending: false,
  isActive: false,
  login: vi.fn(),
  logout: vi.fn(),
}

vi.mock('../context/AuthContext', () => ({
  useAuthContext: () => mockContext,
}))

import useAuth from './useAuth'

beforeEach(() => {
  mockContext.user = null
})

describe('useAuth', () => {
  describe('hasRole', () => {
    it('should return true when user has matching role', () => {
      mockContext.user = { role: 'admin' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.hasRole('admin')).toBe(true)
    })

    it('should return true when user role is in multiple allowed roles', () => {
      mockContext.user = { role: 'loader' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.hasRole('admin', 'loader')).toBe(true)
    })

    it('should return false when user role does not match', () => {
      mockContext.user = { role: 'loader' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.hasRole('admin')).toBe(false)
    })

    it('should return false when user is null', () => {
      mockContext.user = null
      const { result } = renderHook(() => useAuth())

      expect(result.current.hasRole('admin')).toBe(false)
    })
  })

  describe('canCreate', () => {
    it('should return true for admin', () => {
      mockContext.user = { role: 'admin' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canCreate()).toBe(true)
    })

    it('should return true for loader', () => {
      mockContext.user = { role: 'loader' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canCreate()).toBe(true)
    })

    it('should return false for approver', () => {
      mockContext.user = { role: 'approver' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canCreate()).toBe(false)
    })
  })

  describe('canApprove', () => {
    it('should return true for admin', () => {
      mockContext.user = { role: 'admin' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canApprove()).toBe(true)
    })

    it('should return true for approver', () => {
      mockContext.user = { role: 'approver' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canApprove()).toBe(true)
    })

    it('should return false for loader', () => {
      mockContext.user = { role: 'loader' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canApprove()).toBe(false)
    })
  })

  describe('canAdmin', () => {
    it('should return true only for admin', () => {
      mockContext.user = { role: 'admin' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canAdmin()).toBe(true)
    })

    it('should return false for non-admin roles', () => {
      const role = faker.helpers.arrayElement(['loader', 'approver'])
      mockContext.user = { role }
      const { result } = renderHook(() => useAuth())

      expect(result.current.canAdmin()).toBe(false)
    })
  })

  describe('roleLabel', () => {
    it('should return "Administrador" for admin', () => {
      mockContext.user = { role: 'admin' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.roleLabel()).toBe('Administrador')
    })

    it('should return "Cargador" for loader', () => {
      mockContext.user = { role: 'loader' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.roleLabel()).toBe('Cargador')
    })

    it('should return "Aprobador" for approver', () => {
      mockContext.user = { role: 'approver' }
      const { result } = renderHook(() => useAuth())

      expect(result.current.roleLabel()).toBe('Aprobador')
    })

    it('should return "Sin rol" when user has no role', () => {
      mockContext.user = { role: null }
      const { result } = renderHook(() => useAuth())

      expect(result.current.roleLabel()).toBe('Sin rol')
    })

    it('should return "Sin rol" when user is null', () => {
      mockContext.user = null
      const { result } = renderHook(() => useAuth())

      expect(result.current.roleLabel()).toBe('Sin rol')
    })
  })

  describe('context pass-through', () => {
    it('should expose login and logout from context', () => {
      const { result } = renderHook(() => useAuth())

      expect(result.current.login).toBe(mockContext.login)
      expect(result.current.logout).toBe(mockContext.logout)
    })
  })
})
