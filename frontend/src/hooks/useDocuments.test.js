import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { makeDocument, faker } from '../test/helpers'

const mockList = vi.fn()

vi.mock('../api/documents', () => ({
  documentsApi: {
    list: (...args) => mockList(...args),
  },
}))

import useDocuments from './useDocuments'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('useDocuments', () => {
  describe('fetch', () => {
    it('should load documents on mount', async () => {
      const items = [makeDocument(), makeDocument()]
      mockList.mockResolvedValue({
        data: { items, total: 2, total_pages: 1 },
      })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.documents).toEqual(items)
      expect(result.current.total).toBe(2)
      expect(result.current.totalPages).toBe(1)
      expect(result.current.error).toBeNull()
    })

    it('should strip empty/null filter values', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 1 },
      })

      renderHook(() => useDocuments({ type: '', status: null }))

      await waitFor(() => {
        expect(mockList).toHaveBeenCalled()
      })

      const calledWith = mockList.mock.calls[0][0]
      expect(calledWith).not.toHaveProperty('type')
      expect(calledWith).not.toHaveProperty('status')
      expect(calledWith).toHaveProperty('page', 1)
      expect(calledWith).toHaveProperty('page_size', 10)
    })
  })

  describe('error handling', () => {
    it('should set error from API response detail', async () => {
      const detail = faker.lorem.sentence()
      mockList.mockRejectedValue({
        response: { data: { detail } },
      })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe(detail)
      expect(result.current.documents).toEqual([])
    })

    it('should set fallback error when no detail in response', async () => {
      mockList.mockRejectedValue(new Error('Network error'))

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe('Error al cargar documentos')
    })
  })

  describe('updateFilter', () => {
    it('should reset page to 1 when changing a non-page filter', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 1 },
      })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.updateFilter('type', 'invoice')
      })

      expect(result.current.filters.type).toBe('invoice')
      expect(result.current.filters.page).toBe(1)
    })

    it('should update page directly when key is page', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 5 },
      })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.updateFilter('page', 3)
      })

      expect(result.current.filters.page).toBe(3)
    })
  })

  describe('refresh', () => {
    it('should re-fetch documents', async () => {
      const firstItems = [makeDocument()]
      const secondItems = [makeDocument(), makeDocument()]

      mockList
        .mockResolvedValueOnce({ data: { items: firstItems, total: 1, total_pages: 1 } })
        .mockResolvedValueOnce({ data: { items: secondItems, total: 2, total_pages: 1 } })

      const { result } = renderHook(() => useDocuments())

      await waitFor(() => {
        expect(result.current.documents).toEqual(firstItems)
      })

      await act(async () => {
        result.current.refresh()
      })

      await waitFor(() => {
        expect(result.current.documents).toEqual(secondItems)
      })
    })
  })
})
