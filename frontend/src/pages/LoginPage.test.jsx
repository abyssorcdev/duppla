import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

vi.mock('../api/auth', () => ({
  authApi: { loginWithGoogle: vi.fn() },
}))

import LoginPage from './LoginPage'
import { authApi } from '../api/auth'

describe('LoginPage', () => {
  it('renders the app name "Duppla"', () => {
    render(<LoginPage />)
    expect(screen.getByText('Duppla')).toBeInTheDocument()
  })

  it('renders the login button', () => {
    render(<LoginPage />)
    expect(
      screen.getByRole('button', { name: /Continuar con Google/ }),
    ).toBeInTheDocument()
  })

  it('calls authApi.loginWithGoogle when button is clicked', () => {
    render(<LoginPage />)
    fireEvent.click(screen.getByRole('button', { name: /Continuar con Google/ }))
    expect(authApi.loginWithGoogle).toHaveBeenCalledOnce()
  })

  it('renders the terms of use notice', () => {
    render(<LoginPage />)
    expect(
      screen.getByText(/Al iniciar sesión aceptas/),
    ).toBeInTheDocument()
  })
})
