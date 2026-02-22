import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { faker } from '../../test/helpers'
import StatusBadge from './StatusBadge'

const KNOWN_STATUSES = [
  { key: 'draft', label: 'Borrador', colorClass: 'bg-brand-100' },
  { key: 'pending', label: 'En revisión', colorClass: 'bg-amber-100' },
  { key: 'approved', label: 'Aprobado', colorClass: 'bg-green-100' },
  { key: 'rejected', label: 'Rechazado', colorClass: 'bg-red-100' },
]

describe('StatusBadge', () => {
  it.each(KNOWN_STATUSES)(
    'renders "$label" for status "$key"',
    ({ key, label, colorClass }) => {
      render(<StatusBadge status={key} />)
      const badge = screen.getByText(label)
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveClass(colorClass)
    },
  )

  it('falls back to raw status text and gray color for unknown status', () => {
    const unknown = faker.string.alpha(8)
    render(<StatusBadge status={unknown} />)
    const badge = screen.getByText(unknown)
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-600')
  })

  it('renders with default sm size', () => {
    render(<StatusBadge status="draft" />)
    const badge = screen.getByText('Borrador')
    expect(badge).toHaveClass('px-2', 'text-xs')
  })

  it('renders with lg size', () => {
    render(<StatusBadge status="draft" size="lg" />)
    const badge = screen.getByText('Borrador')
    expect(badge).toHaveClass('px-3', 'py-1', 'text-sm')
  })
})
