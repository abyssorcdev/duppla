import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { faker } from '../../test/helpers'
import LoadingSpinner from './LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default size (md) and no text', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('h-8', 'w-8')
    expect(container.querySelector('p')).not.toBeInTheDocument()
  })

  it('renders with size sm', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-5', 'w-5')
  })

  it('renders with size lg', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('h-12', 'w-12')
  })

  it('renders text when provided', () => {
    const text = faker.lorem.sentence()
    render(<LoadingSpinner text={text} />)
    expect(screen.getByText(text)).toBeInTheDocument()
  })

  it('does not render text when empty string is passed', () => {
    const { container } = render(<LoadingSpinner text="" />)
    expect(container.querySelector('p')).not.toBeInTheDocument()
  })
})
