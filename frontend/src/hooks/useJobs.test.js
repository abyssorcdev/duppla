import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { makeJob, faker } from '../test/helpers'

const mockList = vi.fn()

vi.mock('../api/jobs', () => ({
  jobsApi: {
    list: (...args) => mockList(...args),
  },
}))

import useJobs from './useJobs'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('useJobs', () => {
  describe('fetch', () => {
    it('should load jobs on mount', async () => {
      const items = [makeJob(), makeJob()]
      mockList.mockResolvedValue({
        data: { items, total: 2, total_pages: 1 },
      })

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.jobs).toEqual(items)
      expect(result.current.total).toBe(2)
      expect(result.current.totalPages).toBe(1)
      expect(result.current.error).toBeNull()
    })

    it('should strip empty/null filter values', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 1 },
      })

      renderHook(() => useJobs({ status: '', extra: null }))

      await waitFor(() => {
        expect(mockList).toHaveBeenCalled()
      })

      const calledWith = mockList.mock.calls[0][0]
      expect(calledWith).not.toHaveProperty('status')
      expect(calledWith).not.toHaveProperty('extra')
      expect(calledWith).toHaveProperty('page', 1)
    })
  })

  describe('error handling', () => {
    it('should set error from API response detail', async () => {
      const detail = faker.lorem.sentence()
      mockList.mockRejectedValue({
        response: { data: { detail } },
      })

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe(detail)
    })

    it('should set fallback error when no detail', async () => {
      mockList.mockRejectedValue(new Error('fail'))

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.error).toBe('Error al cargar jobs')
    })
  })

  describe('updateFilter', () => {
    it('should reset page to 1 when changing non-page filter', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 1 },
      })

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.updateFilter('status', 'completed')
      })

      expect(result.current.filters.status).toBe('completed')
      expect(result.current.filters.page).toBe(1)
    })

    it('should update page directly when key is page', async () => {
      mockList.mockResolvedValue({
        data: { items: [], total: 0, total_pages: 5 },
      })

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      act(() => {
        result.current.updateFilter('page', 4)
      })

      expect(result.current.filters.page).toBe(4)
    })
  })

  describe('refresh', () => {
    it('should re-fetch jobs', async () => {
      const first = [makeJob()]
      const second = [makeJob(), makeJob()]

      mockList
        .mockResolvedValueOnce({ data: { items: first, total: 1, total_pages: 1 } })
        .mockResolvedValueOnce({ data: { items: second, total: 2, total_pages: 1 } })

      const { result } = renderHook(() => useJobs())

      await waitFor(() => {
        expect(result.current.jobs).toEqual(first)
      })

      await act(async () => {
        result.current.refresh()
      })

      await waitFor(() => {
        expect(result.current.jobs).toEqual(second)
      })
    })
  })
})
