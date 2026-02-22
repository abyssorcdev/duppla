import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'

let matchMediaListeners = []

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
  matchMediaListeners = []

  vi.stubGlobal('matchMedia', vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    addEventListener: (_evt, cb) => { matchMediaListeners.push(cb) },
    removeEventListener: vi.fn(),
  })))
})

import useTheme from './useTheme'

describe('useTheme', () => {
  describe('initial theme', () => {
    it('should default to light when no preference stored', () => {
      const { result } = renderHook(() => useTheme())

      expect(result.current.theme).toBe('light')
      expect(result.current.isDark).toBe(false)
    })

    it('should restore theme from localStorage', () => {
      localStorage.setItem('duppla-theme', 'dark')

      const { result } = renderHook(() => useTheme())

      expect(result.current.theme).toBe('dark')
      expect(result.current.isDark).toBe(true)
    })

    it('should use system preference when no stored value', () => {
      window.matchMedia.mockImplementation((query) => ({
        matches: true,
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }))

      const { result } = renderHook(() => useTheme())

      expect(result.current.theme).toBe('dark')
    })
  })

  describe('toggle', () => {
    it('should switch from light to dark', () => {
      const { result } = renderHook(() => useTheme())

      act(() => {
        result.current.toggle()
      })

      expect(result.current.theme).toBe('dark')
      expect(result.current.isDark).toBe(true)
      expect(localStorage.getItem('duppla-theme')).toBe('dark')
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })

    it('should switch from dark to light', () => {
      localStorage.setItem('duppla-theme', 'dark')

      const { result } = renderHook(() => useTheme())

      act(() => {
        result.current.toggle()
      })

      expect(result.current.theme).toBe('light')
      expect(result.current.isDark).toBe(false)
      expect(localStorage.getItem('duppla-theme')).toBe('light')
      expect(document.documentElement.classList.contains('dark')).toBe(false)
    })
  })

  describe('system preference change', () => {
    it('should react to system preference when no stored value', () => {
      const { result } = renderHook(() => useTheme())

      expect(result.current.theme).toBe('light')

      localStorage.removeItem('duppla-theme')

      act(() => {
        matchMediaListeners.forEach((cb) => cb({ matches: true }))
      })

      expect(result.current.theme).toBe('dark')
    })

    it('should set light theme when system preference changes to light and no stored value', () => {
      window.matchMedia.mockImplementation((query) => ({
        matches: true,
        media: query,
        addEventListener: (_evt, cb) => { matchMediaListeners.push(cb) },
        removeEventListener: vi.fn(),
      }))

      const { result } = renderHook(() => useTheme())

      expect(result.current.theme).toBe('dark')

      localStorage.removeItem('duppla-theme')

      act(() => {
        matchMediaListeners.forEach((cb) => cb({ matches: false }))
      })

      expect(result.current.theme).toBe('light')
      expect(document.documentElement.classList.contains('dark')).toBe(false)
    })

    it('should ignore system preference when user has stored preference', () => {
      localStorage.setItem('duppla-theme', 'light')

      const { result } = renderHook(() => useTheme())

      act(() => {
        matchMediaListeners.forEach((cb) => cb({ matches: true }))
      })

      expect(result.current.theme).toBe('light')
    })
  })
})
