import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'
import { faker } from '../../test/helpers'

vi.mock('../../hooks/useAuth')
import useAuth from '../../hooks/useAuth'

function renderWithRouter(ui, { initialEntry = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/" element={ui} />
        <Route path="/login" element={<div>Login Page</div>} />
        <Route path="/pending" element={<div>Pending Page</div>} />
        <Route path="/403" element={<div>Forbidden Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('redirects to /login when not authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      isPending: false,
      hasRole: vi.fn(() => true),
    })

    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Login Page')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('redirects to /pending when user isPending', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: true,
      hasRole: vi.fn(() => true),
    })

    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Pending Page')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('redirects to /403 when role is not matched', () => {
    const requiredRole = faker.helpers.arrayElement(['admin', 'approver'])
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: false,
      hasRole: vi.fn(() => false),
    })

    renderWithRouter(
      <ProtectedRoute roles={[requiredRole]}>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Forbidden Page')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated and no roles required', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: false,
      hasRole: vi.fn(() => true),
    })

    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('renders children when authenticated and role matches', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: false,
      hasRole: vi.fn(() => true),
    })

    renderWithRouter(
      <ProtectedRoute roles={['admin']}>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('calls hasRole with the spread roles array', () => {
    const hasRole = vi.fn(() => true)
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: false,
      hasRole,
    })

    const roles = ['admin', 'loader']
    renderWithRouter(
      <ProtectedRoute roles={roles}>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(hasRole).toHaveBeenCalledWith('admin', 'loader')
  })

  it('does not call hasRole when roles prop is not provided', () => {
    const hasRole = vi.fn()
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: false,
      hasRole,
    })

    renderWithRouter(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(hasRole).not.toHaveBeenCalled()
    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('checks authentication before pending status', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      isPending: true,
      hasRole: vi.fn(() => false),
    })

    renderWithRouter(
      <ProtectedRoute roles={['admin']}>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })

  it('checks pending before role check', () => {
    const hasRole = vi.fn()
    useAuth.mockReturnValue({
      isAuthenticated: true,
      isPending: true,
      hasRole,
    })

    renderWithRouter(
      <ProtectedRoute roles={['admin']}>
        <div>Protected Content</div>
      </ProtectedRoute>
    )

    expect(screen.getByText('Pending Page')).toBeInTheDocument()
    expect(hasRole).not.toHaveBeenCalled()
  })
})
