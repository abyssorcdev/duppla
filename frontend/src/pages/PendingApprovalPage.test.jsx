import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { makeUser } from '../test/helpers'

const mockNavigate = vi.fn()
const mockLogout = vi.fn()
const fakeUser = makeUser({ status: 'pending' })

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}))

vi.mock('../hooks/useAuth', () => ({
  default: vi.fn(() => ({ user: fakeUser, logout: mockLogout })),
}))

import PendingApprovalPage from './PendingApprovalPage'

describe('PendingApprovalPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the user email', () => {
    render(<PendingApprovalPage />)
    const emails = screen.getAllByText(fakeUser.email)
    expect(emails.length).toBeGreaterThanOrEqual(1)
  })

  it('renders the user name', () => {
    render(<PendingApprovalPage />)
    expect(screen.getByText(fakeUser.name)).toBeInTheDocument()
  })

  it('renders the user picture', () => {
    const { container } = render(<PendingApprovalPage />)
    const img = container.querySelector('img')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', fakeUser.picture)
  })

  it('renders "Cuenta en revisión" heading', () => {
    render(<PendingApprovalPage />)
    expect(screen.getByText('Cuenta en revisión')).toBeInTheDocument()
  })

  it('renders "Esperando aprobación" badge', () => {
    render(<PendingApprovalPage />)
    expect(screen.getByText('Esperando aprobación')).toBeInTheDocument()
  })

  it('calls logout and navigates to /login when logout button is clicked', () => {
    render(<PendingApprovalPage />)
    fireEvent.click(
      screen.getByRole('button', { name: /Cerrar sesión/ }),
    )
    expect(mockLogout).toHaveBeenCalledOnce()
    expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
  })
})
