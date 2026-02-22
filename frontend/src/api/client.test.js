import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { faker } from '../test/helpers'

vi.stubGlobal('localStorage', {
  store: {},
  getItem(key) { return this.store[key] ?? null },
  setItem(key, val) { this.store[key] = val },
  removeItem(key) { delete this.store[key] },
  clear() { this.store = {} },
})

const locationAssign = vi.fn()
vi.stubGlobal('window', {
  ...globalThis.window,
  location: { set href(v) { locationAssign(v) } },
})

let client

beforeEach(async () => {
  vi.resetModules()
  localStorage.clear()
  locationAssign.mockClear()
  const mod = await import('./client.js')
  client = mod.default
})

afterEach(() => {
  vi.unstubAllEnvs()
})

describe('client', () => {
  describe('request interceptor', () => {
    it('should attach Authorization header when token exists', async () => {
      const token = faker.string.alphanumeric(32)
      localStorage.setItem('duppla_token', token)

      const config = await client.interceptors.request.handlers[0].fulfilled({
        headers: {},
      })

      expect(config.headers['Authorization']).toBe(`Bearer ${token}`)
    })

    it('should not attach Authorization header when no token', async () => {
      const config = await client.interceptors.request.handlers[0].fulfilled({
        headers: {},
      })

      expect(config.headers['Authorization']).toBeUndefined()
    })
  })

  describe('response interceptor', () => {
    it('should pass through successful responses', async () => {
      const response = { status: 200, data: { ok: true } }
      const result = await client.interceptors.response.handlers[0].fulfilled(response)

      expect(result).toBe(response)
    })

    it('should clear token and redirect on 401', async () => {
      localStorage.setItem('duppla_token', faker.string.alphanumeric(32))

      const error = { response: { status: 401 } }

      await expect(
        client.interceptors.response.handlers[0].rejected(error)
      ).rejects.toBe(error)

      expect(localStorage.getItem('duppla_token')).toBeNull()
      expect(locationAssign).toHaveBeenCalledWith('/login')
    })

    it('should reject non-401 errors without redirect', async () => {
      const token = faker.string.alphanumeric(32)
      localStorage.setItem('duppla_token', token)

      const error = { response: { status: 500 } }

      await expect(
        client.interceptors.response.handlers[0].rejected(error)
      ).rejects.toBe(error)

      expect(localStorage.getItem('duppla_token')).toBe(token)
    })
  })

  describe('defaults', () => {
    it('should set Content-Type to application/json', () => {
      expect(client.defaults.headers['Content-Type']).toBe('application/json')
    })

    it('should include /api/v1 in baseURL', () => {
      expect(client.defaults.baseURL).toContain('/api/v1')
    })

    it('should use VITE_API_URL when set', async () => {
      vi.stubEnv('VITE_API_URL', 'https://custom-api.example.com')
      vi.resetModules()
      const mod = await import('./client.js')
      expect(mod.default.defaults.baseURL).toBe('https://custom-api.example.com/api/v1')
    })
  })
})
