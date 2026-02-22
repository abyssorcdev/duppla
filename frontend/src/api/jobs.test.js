import { describe, it, expect, vi, beforeEach } from 'vitest'
import { faker, makeJob } from '../test/helpers'

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
  },
}))

import client from './client'
import { jobsApi } from './jobs'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('jobsApi', () => {
  describe('list', () => {
    it('should call GET /jobs without params by default', async () => {
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await jobsApi.list()

      expect(client.get).toHaveBeenCalledWith('/jobs', { params: {} })
    })

    it('should pass filter params to GET /jobs', async () => {
      const items = [makeJob(), makeJob()]
      const params = { status: 'pending', page: 1 }
      client.get.mockResolvedValue({ data: { items, total: 2 } })

      const result = await jobsApi.list(params)

      expect(client.get).toHaveBeenCalledWith('/jobs', { params })
      expect(result.data.items).toHaveLength(2)
    })
  })

  describe('get', () => {
    it('should call GET /jobs/:jobId', async () => {
      const job = makeJob()
      client.get.mockResolvedValue({ data: job })

      const result = await jobsApi.get(job.job_id)

      expect(client.get).toHaveBeenCalledWith(`/jobs/${job.job_id}`)
      expect(result.data).toEqual(job)
    })
  })
})
