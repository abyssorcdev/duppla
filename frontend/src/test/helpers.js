import { faker } from '@faker-js/faker'

export { faker }

export function makeDocument(overrides = {}) {
  return {
    id: faker.number.int({ min: 1, max: 99999 }),
    type: faker.helpers.arrayElement(['invoice', 'receipt', 'voucher']),
    amount: faker.number.float({ min: 1, max: 999999, fractionDigits: 2 }),
    status: 'draft',
    created_at: faker.date.recent().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    created_by: faker.string.alphanumeric(8),
    metadata: {},
    ...overrides,
  }
}

export function makeUser(overrides = {}) {
  return {
    sub: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: faker.helpers.arrayElement(['admin', 'loader', 'approver']),
    status: 'active',
    picture: faker.image.avatar(),
    exp: Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000),
    ...overrides,
  }
}

export function makeJob(overrides = {}) {
  return {
    job_id: faker.string.uuid(),
    status: 'pending',
    document_ids: [
      faker.number.int({ min: 1, max: 999 }),
      faker.number.int({ min: 1, max: 999 }),
    ],
    created_at: faker.date.recent().toISOString(),
    completed_at: null,
    result: null,
    error_message: null,
    ...overrides,
  }
}

/**
 * Build a fake JWT string from a payload object.
 * No real signature — only the base64-encoded payload matters for client-side decoding.
 */
export function makeJwt(payload = {}) {
  const defaults = makeUser()
  const merged = { ...defaults, ...payload }
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = btoa(JSON.stringify(merged))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')
  return `${header}.${body}.fake-signature`
}
