import { describe, it, expect, vi, beforeEach } from 'vitest'
import { faker, makeUser } from '../test/helpers'

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

import client from './client'
import { adminApi } from './admin'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('adminApi', () => {
  describe('listUsers', () => {
    it('should call GET /admin/users without params by default', async () => {
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await adminApi.listUsers()

      expect(client.get).toHaveBeenCalledWith('/admin/users', { params: {} })
    })

    it('should pass filter params', async () => {
      const params = { status: 'pending', page: 2 }
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await adminApi.listUsers(params)

      expect(client.get).toHaveBeenCalledWith('/admin/users', { params })
    })
  })

  describe('approveUser', () => {
    it('should call PATCH /admin/users/:id/approve with role', async () => {
      const userId = faker.string.uuid()
      const role = faker.helpers.arrayElement(['admin', 'loader', 'approver'])
      client.patch.mockResolvedValue({ data: makeUser({ sub: userId, role }) })

      await adminApi.approveUser(userId, role)

      expect(client.patch).toHaveBeenCalledWith(
        `/admin/users/${userId}/approve`,
        { role },
      )
    })
  })

  describe('disableUser', () => {
    it('should call PATCH /admin/users/:id/disable', async () => {
      const userId = faker.string.uuid()
      client.patch.mockResolvedValue({ data: {} })

      await adminApi.disableUser(userId)

      expect(client.patch).toHaveBeenCalledWith(`/admin/users/${userId}/disable`)
    })
  })

  describe('listLogs', () => {
    it('should call GET /admin/logs without params by default', async () => {
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await adminApi.listLogs()

      expect(client.get).toHaveBeenCalledWith('/admin/logs', { params: {} })
    })

    it('should pass filter params', async () => {
      const params = { page: 3, page_size: 25 }
      client.get.mockResolvedValue({ data: { items: [], total: 0 } })

      await adminApi.listLogs(params)

      expect(client.get).toHaveBeenCalledWith('/admin/logs', { params })
    })
  })
})
