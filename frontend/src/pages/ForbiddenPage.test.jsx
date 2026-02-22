import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ForbiddenPage from './ForbiddenPage'

describe('ForbiddenPage', () => {
  it('renders "Sin permisos" heading', () => {
    render(<ForbiddenPage />, { wrapper: BrowserRouter })
    expect(screen.getByText('Sin permisos')).toBeInTheDocument()
  })

  it('renders an explanatory paragraph', () => {
    render(<ForbiddenPage />, { wrapper: BrowserRouter })
    expect(
      screen.getByText(/No tienes el rol necesario/),
    ).toBeInTheDocument()
  })

  it('has a link pointing to "/"', () => {
    render(<ForbiddenPage />, { wrapper: BrowserRouter })
    const link = screen.getByRole('link', { name: /Volver al inicio/ })
    expect(link).toHaveAttribute('href', '/')
  })
})
