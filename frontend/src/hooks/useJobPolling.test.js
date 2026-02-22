import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { makeJob, faker } from '../test/helpers'

const mockGet = vi.fn()

vi.mock('../api/jobs', () => ({
  jobsApi: {
    get: (...args) => mockGet(...args),
  },
}))

import useJobPolling from './useJobPolling'

beforeEach(() => {
  vi.useFakeTimers()
  vi.clearAllMocks()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('useJobPolling', () => {
  describe('initial fetch', () => {
    it('should fetch job immediately on mount', async () => {
      const job = makeJob()
      mockGet.mockResolvedValue({ data: job })

      const { result } = renderHook(() => useJobPolling(job.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(mockGet).toHaveBeenCalledWith(job.job_id)
      expect(result.current.job).toEqual(job)
      expect(result.current.loading).toBe(false)
    })

    it('should not fetch when jobId is null', () => {
      renderHook(() => useJobPolling(null))

      expect(mockGet).not.toHaveBeenCalled()
    })
  })

  describe('polling', () => {
    it('should poll every 3 seconds', async () => {
      const job = makeJob({ status: 'pending' })
      mockGet.mockResolvedValue({ data: job })

      renderHook(() => useJobPolling(job.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(mockGet).toHaveBeenCalledTimes(1)

      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(mockGet).toHaveBeenCalledTimes(2)

      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(mockGet).toHaveBeenCalledTimes(3)
    })
  })

  describe('terminal states', () => {
    it('should stop polling when job status is completed', async () => {
      const pending = makeJob({ status: 'pending' })
      const completed = makeJob({ status: 'completed' })

      mockGet
        .mockResolvedValueOnce({ data: pending })
        .mockResolvedValueOnce({ data: completed })

      const { result } = renderHook(() => useJobPolling(pending.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(result.current.job.status).toBe('completed')
      expect(result.current.isPolling).toBe(false)

      const callCount = mockGet.mock.calls.length
      await act(async () => {
        await vi.advanceTimersByTimeAsync(6000)
      })

      expect(mockGet).toHaveBeenCalledTimes(callCount)
    })

    it('should stop polling when job status is failed', async () => {
      const failed = makeJob({ status: 'failed', error_message: faker.lorem.sentence() })
      mockGet.mockResolvedValue({ data: failed })

      const { result } = renderHook(() => useJobPolling(failed.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(result.current.job.status).toBe('failed')
      expect(result.current.isPolling).toBe(false)
    })
  })

  describe('error handling', () => {
    it('should stop polling after 3 consecutive errors', async () => {
      const job = makeJob()
      const errorDetail = faker.lorem.sentence()
      const apiError = { response: { data: { detail: errorDetail } } }

      mockGet.mockRejectedValue(apiError)

      const { result } = renderHook(() => useJobPolling(job.job_id))

      // 1st error
      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(result.current.error).toBeNull()

      // 2nd error
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(result.current.error).toBeNull()

      // 3rd error → stops
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(result.current.error).toBe(errorDetail)
      expect(result.current.isPolling).toBe(false)
    })

    it('should use fallback error message when response has no detail', async () => {
      const job = makeJob()
      mockGet.mockRejectedValue(new Error('network'))

      const { result } = renderHook(() => useJobPolling(job.job_id))

      await act(async () => { await vi.advanceTimersByTimeAsync(0) })
      await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
      await act(async () => { await vi.advanceTimersByTimeAsync(3000) })

      expect(result.current.error).toBe('Error al consultar el job')
      expect(result.current.isPolling).toBe(false)
    })

    it('should reset error count on successful fetch', async () => {
      const job = makeJob({ status: 'pending' })

      mockGet
        .mockRejectedValueOnce(new Error('fail'))
        .mockRejectedValueOnce(new Error('fail'))
        .mockResolvedValueOnce({ data: job })
        .mockRejectedValueOnce(new Error('fail'))
        .mockRejectedValueOnce(new Error('fail'))

      const { result } = renderHook(() => useJobPolling(job.job_id))

      // 2 errors, then success
      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(result.current.error).toBeNull()
      expect(result.current.job).toEqual(job)

      // 2 more errors (count reset, so no stop yet)
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })
      await act(async () => {
        await vi.advanceTimersByTimeAsync(3000)
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('visibilitychange', () => {
    it('should re-fetch when document becomes visible', async () => {
      const job = makeJob({ status: 'pending' })
      mockGet.mockResolvedValue({ data: job })

      renderHook(() => useJobPolling(job.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      const callsBefore = mockGet.mock.calls.length

      Object.defineProperty(document, 'visibilityState', { value: 'visible', writable: true })

      await act(async () => {
        document.dispatchEvent(new Event('visibilitychange'))
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(mockGet.mock.calls.length).toBeGreaterThan(callsBefore)
    })

    it('should NOT re-fetch on visibilitychange when job is in terminal state', async () => {
      const job = makeJob({ status: 'completed' })
      mockGet.mockResolvedValue({ data: job })

      renderHook(() => useJobPolling(job.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      const callsAfterTerminal = mockGet.mock.calls.length

      Object.defineProperty(document, 'visibilityState', { value: 'visible', writable: true })

      await act(async () => {
        document.dispatchEvent(new Event('visibilitychange'))
        await vi.advanceTimersByTimeAsync(0)
      })

      expect(mockGet).toHaveBeenCalledTimes(callsAfterTerminal)
    })
  })

  describe('cleanup', () => {
    it('should stop polling on unmount', async () => {
      const job = makeJob({ status: 'pending' })
      mockGet.mockResolvedValue({ data: job })

      const { unmount } = renderHook(() => useJobPolling(job.job_id))

      await act(async () => {
        await vi.advanceTimersByTimeAsync(0)
      })

      unmount()

      const callCount = mockGet.mock.calls.length
      await act(async () => {
        await vi.advanceTimersByTimeAsync(6000)
      })

      expect(mockGet).toHaveBeenCalledTimes(callCount)
    })
  })
})
