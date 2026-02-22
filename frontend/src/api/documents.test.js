import { describe, it, expect, vi, beforeEach } from 'vitest'
import { faker, makeDocument } from '../test/helpers'

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
  },
}))

import client from './client'
import { documentsApi } from './documents'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('documentsApi', () => {
  describe('list', () => {
    it('should call GET /documents without params by default', async () => {
      const items = [makeDocument(), makeDocument()]
      client.get.mockResolvedValue({ data: { items, total: 2 } })

      await documentsApi.list()

      expect(client.get).toHaveBeenCalledWith('/documents', { params: {} })
    })

    it('should pass filter params to GET /documents', async () => {
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })
      const params = { type: 'invoice', page: 2 }

      await documentsApi.list(params)

      expect(client.get).toHaveBeenCalledWith('/documents', { params })
    })
  })

  describe('get', () => {
    it('should call GET /documents/:id', async () => {
      const doc = makeDocument()
      client.get.mockResolvedValue({ data: doc })

      const result = await documentsApi.get(doc.id)

      expect(client.get).toHaveBeenCalledWith(`/documents/${doc.id}`)
      expect(result.data).toEqual(doc)
    })
  })

  describe('create', () => {
    it('should call POST /documents with data', async () => {
      const data = {
        type: faker.helpers.arrayElement(['invoice', 'receipt']),
        amount: faker.number.float({ min: 1, max: 9999, fractionDigits: 2 }),
      }
      const created = makeDocument(data)
      client.post.mockResolvedValue({ data: created })

      const result = await documentsApi.create(data)

      expect(client.post).toHaveBeenCalledWith('/documents', data)
      expect(result.data.type).toBe(data.type)
    })
  })

  describe('update', () => {
    it('should call PUT /documents/:id with data', async () => {
      const doc = makeDocument()
      const update = { amount: faker.number.float({ min: 1, max: 9999, fractionDigits: 2 }) }
      client.put.mockResolvedValue({ data: { ...doc, ...update } })

      await documentsApi.update(doc.id, update)

      expect(client.put).toHaveBeenCalledWith(`/documents/${doc.id}`, update)
    })
  })

  describe('changeStatus', () => {
    it('should call PATCH /documents/:id/status with new_status', async () => {
      const id = faker.number.int({ min: 1, max: 99999 })
      client.patch.mockResolvedValue({ data: {} })

      await documentsApi.changeStatus(id, 'pending')

      expect(client.patch).toHaveBeenCalledWith(`/documents/${id}/status`, {
        new_status: 'pending',
      })
    })

    it('should include comment when provided', async () => {
      const id = faker.number.int({ min: 1, max: 99999 })
      const comment = faker.lorem.sentence()
      client.patch.mockResolvedValue({ data: {} })

      await documentsApi.changeStatus(id, 'rejected', comment)

      expect(client.patch).toHaveBeenCalledWith(`/documents/${id}/status`, {
        new_status: 'rejected',
        comment,
      })
    })

    it('should not include comment key when null', async () => {
      const id = faker.number.int({ min: 1, max: 99999 })
      client.patch.mockResolvedValue({ data: {} })

      await documentsApi.changeStatus(id, 'approved', null)

      const payload = client.patch.mock.calls[0][1]
      expect(payload).not.toHaveProperty('comment')
    })
  })

  describe('processBatch', () => {
    it('should call POST /documents/batch/process with document_ids', async () => {
      const ids = [
        faker.number.int({ min: 1, max: 999 }),
        faker.number.int({ min: 1, max: 999 }),
      ]
      client.post.mockResolvedValue({ data: { job_id: faker.string.uuid() } })

      await documentsApi.processBatch(ids)

      expect(client.post).toHaveBeenCalledWith('/documents/batch/process', {
        document_ids: ids,
      })
    })
  })
})
