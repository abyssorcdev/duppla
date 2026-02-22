import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from './Sidebar'
import { makeUser, faker } from '../../test/helpers'

const mockLogout = vi.fn()
const mockToggle = vi.fn()
const mockNavigate = vi.fn()
let mockUser = null
let mockCanAdmin = vi.fn(() => false)
let mockIsDark = false

vi.mock('../../hooks/useAuth', () => ({
  default: () => ({
    user: mockUser,
    logout: mockLogout,
    canAdmin: mockCanAdmin,
  }),
}))

vi.mock('../../hooks/useTheme', () => ({
  default: () => ({
    isDark: mockIsDark,
    toggle: mockToggle,
  }),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

beforeEach(() => {
  vi.clearAllMocks()
  mockUser = makeUser({ role: 'loader' })
  mockCanAdmin = vi.fn(() => false)
  mockIsDark = false
})

function renderSidebar(route = '/') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Sidebar />
    </MemoryRouter>,
  )
}

describe('Sidebar', () => {
  describe('navigation links', () => {
    it('should render common nav links', () => {
      renderSidebar()

      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Documentos')).toBeInTheDocument()
      expect(screen.getByText('Jobs')).toBeInTheDocument()
    })

    it('should show admin link only for admin role', () => {
      mockCanAdmin = vi.fn(() => true)
      renderSidebar()

      expect(screen.getByText('Administración')).toBeInTheDocument()
    })

    it('should hide admin link for non-admin roles', () => {
      mockCanAdmin = vi.fn(() => false)
      renderSidebar()

      expect(screen.queryByText('Administración')).not.toBeInTheDocument()
    })
  })

  describe('user info', () => {
    it('should render user picture as img when present', () => {
      const picture = faker.image.avatar()
      mockUser = makeUser({ picture })
      renderSidebar()

      const img = screen.getByRole('presentation')
      expect(img.tagName).toBe('IMG')
      expect(img).toHaveAttribute('src', picture)
    })

    it('should render initial when user has no picture', () => {
      const name = faker.person.fullName()
      mockUser = makeUser({ picture: null, name })
      renderSidebar()

      expect(screen.getByText(name.charAt(0).toUpperCase())).toBeInTheDocument()
    })

    it('should display user name', () => {
      const name = faker.person.fullName()
      mockUser = makeUser({ name })
      renderSidebar()

      expect(screen.getByText(name)).toBeInTheDocument()
    })

    it('should display role label for loader', () => {
      mockUser = makeUser({ role: 'loader' })
      renderSidebar()

      expect(screen.getByText('Cargador')).toBeInTheDocument()
    })

    it('should display role label for admin', () => {
      mockUser = makeUser({ role: 'admin' })
      renderSidebar()

      expect(screen.getByText('Administrador')).toBeInTheDocument()
    })

    it('should display role label for approver', () => {
      mockUser = makeUser({ role: 'approver' })
      renderSidebar()

      expect(screen.getByText('Aprobador')).toBeInTheDocument()
    })

    it('should display fallback label for unknown role', () => {
      mockUser = makeUser({ role: 'unknown' })
      renderSidebar()

      expect(screen.getByText('Sin rol')).toBeInTheDocument()
    })
  })

  describe('theme toggle', () => {
    it('should show dark mode button text when theme is light', () => {
      mockIsDark = false
      renderSidebar()

      expect(screen.getByText('Modo oscuro')).toBeInTheDocument()
    })

    it('should show light mode button text when theme is dark', () => {
      mockIsDark = true
      renderSidebar()

      expect(screen.getByText('Modo claro')).toBeInTheDocument()
    })

    it('should call toggle when theme button is clicked', async () => {
      const user = userEvent.setup()
      renderSidebar()

      await user.click(screen.getByText('Modo oscuro'))

      expect(mockToggle).toHaveBeenCalled()
    })
  })

  describe('logout', () => {
    it('should call logout and navigate to /login on logout click', async () => {
      const user = userEvent.setup()
      renderSidebar()

      await user.click(screen.getByText('Cerrar sesión'))

      expect(mockLogout).toHaveBeenCalled()
      expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
    })
  })
})
