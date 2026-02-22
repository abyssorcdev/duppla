import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FilterBar from './FilterBar'
import { faker } from '../../test/helpers'

function getControl(labelText) {
  const label = screen.getByText(labelText, { selector: 'label' })
  const wrapper = label.parentElement
  return wrapper.querySelector('select, input, textarea')
}

describe('FilterBar', () => {
  const buildProps = (overrides = {}) => ({
    filters: { type: '', status: '', amount_min: '', amount_max: '' },
    onFilterChange: vi.fn(),
    ...overrides,
  })

  it('renders the type select with "Todos" default', () => {
    render(<FilterBar {...buildProps()} />)
    const select = getControl('Tipo')
    expect(select).toBeInTheDocument()
    expect(select).toHaveValue('')
  })

  it('renders the status select', () => {
    render(<FilterBar {...buildProps()} />)
    const select = getControl('Estado')
    expect(select).toBeInTheDocument()
    expect(select).toHaveValue('')
  })

  it('renders amount min input', () => {
    render(<FilterBar {...buildProps()} />)
    expect(getControl('Monto mínimo')).toBeInTheDocument()
  })

  it('renders amount max input', () => {
    render(<FilterBar {...buildProps()} />)
    expect(getControl('Monto máximo')).toBeInTheDocument()
  })

  it('renders the "Limpiar filtros" button', () => {
    render(<FilterBar {...buildProps()} />)
    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument()
  })

  it('calls onFilterChange with type when type select changes', () => {
    const props = buildProps()
    render(<FilterBar {...props} />)
    fireEvent.change(getControl('Tipo'), { target: { value: 'invoice' } })
    expect(props.onFilterChange).toHaveBeenCalledWith('type', 'invoice')
  })

  it('calls onFilterChange with status when status select changes', () => {
    const props = buildProps()
    render(<FilterBar {...props} />)
    fireEvent.change(getControl('Estado'), { target: { value: 'approved' } })
    expect(props.onFilterChange).toHaveBeenCalledWith('status', 'approved')
  })

  it('calls onFilterChange with amount_min when min input changes', () => {
    const amount = faker.number.int({ min: 100, max: 9999 }).toString()
    const props = buildProps()
    render(<FilterBar {...props} />)
    fireEvent.change(getControl('Monto mínimo'), { target: { value: amount } })
    expect(props.onFilterChange).toHaveBeenCalledWith('amount_min', amount)
  })

  it('calls onFilterChange with amount_max when max input changes', () => {
    const amount = faker.number.int({ min: 100, max: 9999 }).toString()
    const props = buildProps()
    render(<FilterBar {...props} />)
    fireEvent.change(getControl('Monto máximo'), { target: { value: amount } })
    expect(props.onFilterChange).toHaveBeenCalledWith('amount_max', amount)
  })

  it('clears all filters when "Limpiar filtros" is clicked', () => {
    const props = buildProps({
      filters: {
        type: 'invoice',
        status: 'draft',
        amount_min: '100',
        amount_max: '5000',
      },
    })
    render(<FilterBar {...props} />)
    fireEvent.click(screen.getByText('Limpiar filtros'))
    expect(props.onFilterChange).toHaveBeenCalledWith('type', '')
    expect(props.onFilterChange).toHaveBeenCalledWith('status', '')
    expect(props.onFilterChange).toHaveBeenCalledWith('amount_min', '')
    expect(props.onFilterChange).toHaveBeenCalledWith('amount_max', '')
    expect(props.onFilterChange).toHaveBeenCalledTimes(4)
  })

  it('reflects current filter values from props', () => {
    render(
      <FilterBar
        {...buildProps({
          filters: { type: 'receipt', status: 'pending', amount_min: '200', amount_max: '8000' },
        })}
      />
    )
    expect(getControl('Tipo')).toHaveValue('receipt')
    expect(getControl('Estado')).toHaveValue('pending')
    expect(getControl('Monto mínimo')).toHaveValue(200)
    expect(getControl('Monto máximo')).toHaveValue(8000)
  })

  it('renders all type options', () => {
    render(<FilterBar {...buildProps()} />)
    const select = getControl('Tipo')
    expect(select.querySelectorAll('option').length).toBe(6)
  })

  it('renders all status options', () => {
    render(<FilterBar {...buildProps()} />)
    const select = getControl('Estado')
    expect(select.querySelectorAll('option').length).toBe(5)
  })

  it('handles null/undefined filter values via fallback', () => {
    render(
      <FilterBar
        {...buildProps({
          filters: { type: null, status: undefined, amount_min: null, amount_max: undefined },
        })}
      />
    )
    expect(getControl('Tipo')).toHaveValue('')
    expect(getControl('Estado')).toHaveValue('')
    expect(getControl('Monto mínimo')).toHaveValue(null)
    expect(getControl('Monto máximo')).toHaveValue(null)
  })
})
