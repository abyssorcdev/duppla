import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('./pages/LoginPage', () => ({ default: () => <div data-testid="login-page">LoginPage</div> }))
vi.mock('./pages/AuthCallbackPage', () => ({ default: () => <div>AuthCallback</div> }))
vi.mock('./pages/PendingApprovalPage', () => ({ default: () => <div>Pending</div> }))
vi.mock('./pages/ForbiddenPage', () => ({ default: () => <div>Forbidden</div> }))
vi.mock('./pages/DashboardPage', () => ({ default: () => <div>Dashboard</div> }))
vi.mock('./pages/DocumentsPage', () => ({ default: () => <div>Documents</div> }))
vi.mock('./pages/DocumentCreatePage', () => ({ default: () => <div>DocCreate</div> }))
vi.mock('./pages/DocumentDetailPage', () => ({ default: () => <div>DocDetail</div> }))
vi.mock('./pages/JobsPage', () => ({ default: () => <div>Jobs</div> }))
vi.mock('./pages/JobPage', () => ({ default: () => <div>Job</div> }))
vi.mock('./pages/AdminPage', () => ({ default: () => <div>Admin</div> }))
vi.mock('./components/layout/Layout', () => ({ default: () => <div>Layout</div> }))
vi.mock('./components/auth/ProtectedRoute', () => ({
  default: ({ children }) => <div>{children}</div>,
}))
vi.mock('./hooks/useTheme', () => ({
  default: () => ({ theme: 'light', toggle: vi.fn(), isDark: false }),
}))

import App from './App'

describe('App', () => {
  it('should render without crashing', () => {
    render(<App />)

    expect(document.body).toBeTruthy()
  })

  it('should show login page at /login route', () => {
    window.history.pushState({}, '', '/login')

    render(<App />)

    expect(screen.getByTestId('login-page')).toBeInTheDocument()
  })
})
