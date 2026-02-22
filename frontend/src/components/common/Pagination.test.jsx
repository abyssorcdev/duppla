import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Pagination from './Pagination'
import { faker } from '../../test/helpers'

describe('Pagination', () => {
  const buildProps = (overrides = {}) => ({
    page: 1,
    totalPages: faker.number.int({ min: 5, max: 20 }),
    onPageChange: vi.fn(),
    ...overrides,
  })

  it('returns null when totalPages is 0', () => {
    const { container } = render(<Pagination {...buildProps({ totalPages: 0 })} />)
    expect(container.innerHTML).toBe('')
  })

  it('returns null when totalPages is 1', () => {
    const { container } = render(<Pagination {...buildProps({ totalPages: 1 })} />)
    expect(container.innerHTML).toBe('')
  })

  it('renders page buttons for a small range', () => {
    render(<Pagination {...buildProps({ page: 1, totalPages: 3 })} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('disables "Anterior" button on first page', () => {
    render(<Pagination {...buildProps({ page: 1, totalPages: 5 })} />)
    expect(screen.getByText('← Anterior')).toBeDisabled()
  })

  it('enables "Anterior" button when not on first page', () => {
    render(<Pagination {...buildProps({ page: 3, totalPages: 5 })} />)
    expect(screen.getByText('← Anterior')).not.toBeDisabled()
  })

  it('disables "Siguiente" button on last page', () => {
    render(<Pagination {...buildProps({ page: 5, totalPages: 5 })} />)
    expect(screen.getByText('Siguiente →')).toBeDisabled()
  })

  it('enables "Siguiente" button when not on last page', () => {
    render(<Pagination {...buildProps({ page: 3, totalPages: 5 })} />)
    expect(screen.getByText('Siguiente →')).not.toBeDisabled()
  })

  it('calls onPageChange(page - 1) when clicking "Anterior"', () => {
    const props = buildProps({ page: 3, totalPages: 5 })
    render(<Pagination {...props} />)
    fireEvent.click(screen.getByText('← Anterior'))
    expect(props.onPageChange).toHaveBeenCalledWith(2)
  })

  it('calls onPageChange(page + 1) when clicking "Siguiente"', () => {
    const props = buildProps({ page: 3, totalPages: 5 })
    render(<Pagination {...props} />)
    fireEvent.click(screen.getByText('Siguiente →'))
    expect(props.onPageChange).toHaveBeenCalledWith(4)
  })

  it('calls onPageChange(n) when clicking a page button', () => {
    const props = buildProps({ page: 1, totalPages: 5 })
    render(<Pagination {...props} />)
    fireEvent.click(screen.getByText('3'))
    expect(props.onPageChange).toHaveBeenCalledWith(3)
  })

  it('highlights the active page button', () => {
    render(<Pagination {...buildProps({ page: 3, totalPages: 5 })} />)
    const activeBtn = screen.getByText('3')
    expect(activeBtn.className).toContain('bg-brand-700')
    expect(activeBtn.className).toContain('text-white')
  })

  it('does not highlight inactive page buttons', () => {
    render(<Pagination {...buildProps({ page: 3, totalPages: 5 })} />)
    const inactiveBtn = screen.getByText('1')
    expect(inactiveBtn.className).not.toContain('bg-brand-700')
    expect(inactiveBtn.className).toContain('text-brand-700')
  })

  it('shows left ellipsis and page 1 button when left > 2', () => {
    render(<Pagination {...buildProps({ page: 6, totalPages: 10 })} />)
    const allButtons = screen.getAllByRole('button')
    const pageOneBtn = allButtons.find((btn) => btn.textContent === '1')
    expect(pageOneBtn).toBeTruthy()
    expect(screen.getAllByText('…').length).toBeGreaterThanOrEqual(1)
  })

  it('shows page 1 without left ellipsis when left === 2', () => {
    render(<Pagination {...buildProps({ page: 4, totalPages: 10 })} />)
    const allButtons = screen.getAllByRole('button')
    const pageOneBtn = allButtons.find((btn) => btn.textContent === '1')
    expect(pageOneBtn).toBeTruthy()
  })

  it('shows right ellipsis and last page button when right < totalPages - 1', () => {
    render(<Pagination {...buildProps({ page: 5, totalPages: 10 })} />)
    const allButtons = screen.getAllByRole('button')
    const lastBtn = allButtons.find((btn) => btn.textContent === '10')
    expect(lastBtn).toBeTruthy()
    expect(screen.getAllByText('…').length).toBeGreaterThanOrEqual(1)
  })

  it('shows last page without right ellipsis when right === totalPages - 1', () => {
    render(<Pagination {...buildProps({ page: 7, totalPages: 9 })} />)
    const allButtons = screen.getAllByRole('button')
    const lastBtn = allButtons.find((btn) => btn.textContent === '9')
    expect(lastBtn).toBeTruthy()
  })

  it('shows both ellipses when page is in the middle of a large range', () => {
    render(<Pagination {...buildProps({ page: 10, totalPages: 20 })} />)
    const ellipses = screen.getAllByText('…')
    expect(ellipses.length).toBe(2)
  })

  it('shows no ellipsis when totalPages is small', () => {
    render(<Pagination {...buildProps({ page: 2, totalPages: 3 })} />)
    expect(screen.queryByText('…')).toBeNull()
  })
})
