import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

vi.mock('./Sidebar', () => ({
  default: () => <aside data-testid="sidebar">Sidebar</aside>,
}))

vi.mock('react-router-dom', () => ({
  Outlet: () => <div data-testid="outlet">Outlet</div>,
}))

import Layout from './Layout'

describe('Layout', () => {
  it('renders the Sidebar component', () => {
    render(<Layout />)
    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
  })

  it('renders the Outlet component', () => {
    render(<Layout />)
    expect(screen.getByTestId('outlet')).toBeInTheDocument()
  })
})
