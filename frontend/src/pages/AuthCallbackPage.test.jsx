import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { faker } from '../test/helpers'

const mockNavigate = vi.fn()
const mockLogin = vi.fn()
let searchParamsMap = new Map()

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useSearchParams: () => [{ get: (key) => searchParamsMap.get(key) ?? null }],
}))

vi.mock('../hooks/useAuth', () => ({
  default: vi.fn(() => ({ login: mockLogin })),
}))

import AuthCallbackPage from './AuthCallbackPage'

describe('AuthCallbackPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    searchParamsMap = new Map()
  })

  it('navigates to /pending when token is present and status is pending', () => {
    const token = faker.string.alphanumeric(32)
    searchParamsMap.set('token', token)
    searchParamsMap.set('status', 'pending')

    render(<AuthCallbackPage />)

    expect(mockLogin).toHaveBeenCalledWith(token)
    expect(mockNavigate).toHaveBeenCalledWith('/pending', { replace: true })
  })

  it('navigates to / when token is present and status is not pending', () => {
    const token = faker.string.alphanumeric(32)
    searchParamsMap.set('token', token)
    searchParamsMap.set('status', 'active')

    render(<AuthCallbackPage />)

    expect(mockLogin).toHaveBeenCalledWith(token)
    expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true })
  })

  it('navigates to / when token is present with no status', () => {
    const token = faker.string.alphanumeric(32)
    searchParamsMap.set('token', token)

    render(<AuthCallbackPage />)

    expect(mockLogin).toHaveBeenCalledWith(token)
    expect(mockNavigate).toHaveBeenCalledWith('/', { replace: true })
  })

  it('navigates to /login?error=auth_failed when error param is present', () => {
    searchParamsMap.set('error', 'some_error')
    searchParamsMap.set('token', faker.string.alphanumeric(32))

    render(<AuthCallbackPage />)

    expect(mockLogin).not.toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/login?error=auth_failed', {
      replace: true,
    })
  })

  it('navigates to /login?error=auth_failed when no token is present', () => {
    render(<AuthCallbackPage />)

    expect(mockLogin).not.toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith('/login?error=auth_failed', {
      replace: true,
    })
  })

  it('renders the loading spinner text', () => {
    const token = faker.string.alphanumeric(32)
    searchParamsMap.set('token', token)

    render(<AuthCallbackPage />)
    expect(screen.getByText('Iniciando sesión...')).toBeInTheDocument()
  })
})
