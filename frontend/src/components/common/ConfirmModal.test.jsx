import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { faker } from '../../test/helpers'
import ConfirmModal from './ConfirmModal'

function renderModal(overrides = {}) {
  const props = {
    title: faker.lorem.sentence(),
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
    ...overrides,
  }
  const result = render(<ConfirmModal {...props} />)
  return { ...result, props }
}

describe('ConfirmModal', () => {
  it('renders the title', () => {
    const { props } = renderModal()
    expect(screen.getByText(props.title)).toBeInTheDocument()
  })

  it('renders the description when provided', () => {
    const description = faker.lorem.paragraph()
    renderModal({ description })
    expect(screen.getByText(description)).toBeInTheDocument()
  })

  it('does not render a description paragraph when not provided', () => {
    const { props } = renderModal()
    const heading = screen.getByText(props.title)
    const descP = heading.parentElement.querySelector('p')
    expect(descP).not.toBeInTheDocument()
  })

  it('renders children', () => {
    const childText = faker.lorem.word()
    renderModal({ children: <div data-testid="child">{childText}</div> })
    expect(screen.getByTestId('child')).toHaveTextContent(childText)
  })

  it('calls onConfirm when confirm button is clicked', () => {
    const { props } = renderModal()
    fireEvent.click(screen.getByText('Confirmar'))
    expect(props.onConfirm).toHaveBeenCalledOnce()
  })

  it('calls onCancel when cancel button is clicked', () => {
    const { props } = renderModal()
    fireEvent.click(screen.getByText('Cancelar'))
    expect(props.onCancel).toHaveBeenCalledOnce()
  })

  it('uses default confirmLabel "Confirmar"', () => {
    renderModal()
    expect(screen.getByText('Confirmar')).toBeInTheDocument()
  })

  it('renders custom confirmLabel', () => {
    const label = faker.lorem.word()
    renderModal({ confirmLabel: label })
    expect(screen.getByText(label)).toBeInTheDocument()
  })

  it('applies custom confirmClass to confirm button', () => {
    const cls = 'bg-blue-600 hover:bg-blue-700'
    renderModal({ confirmClass: cls })
    const btn = screen.getByText('Confirmar')
    expect(btn).toHaveClass('bg-blue-600')
  })

  it('applies default confirmClass (red) when not overridden', () => {
    renderModal()
    const btn = screen.getByText('Confirmar')
    expect(btn).toHaveClass('bg-red-600')
  })

  it('shows "Procesando..." and disables buttons when loading', () => {
    const { props } = renderModal({ loading: true })
    expect(screen.getByText('Procesando...')).toBeInTheDocument()
    expect(screen.queryByText(props.confirmLabel || 'Confirmar')).not.toBeInTheDocument()

    const buttons = screen.getAllByRole('button')
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled()
    })
  })

  it('buttons are enabled when not loading', () => {
    renderModal({ loading: false })
    const buttons = screen.getAllByRole('button')
    buttons.forEach((btn) => {
      expect(btn).toBeEnabled()
    })
  })
})
