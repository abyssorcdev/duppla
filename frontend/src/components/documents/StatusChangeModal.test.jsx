import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import StatusChangeModal from './StatusChangeModal'
import { faker, makeDocument } from '../../test/helpers'

beforeEach(() => {
  vi.clearAllMocks()
})

function renderModal(overrides = {}) {
  const doc = makeDocument({ status: 'pending', ...overrides.document })
  const onClose = vi.fn()
  const onSuccess = vi.fn()

  const utils = render(
    <StatusChangeModal
      document={doc}
      onClose={overrides.onClose ?? onClose}
      onSuccess={overrides.onSuccess ?? onSuccess}
    />,
  )

  return { ...utils, doc, onClose, onSuccess }
}

describe('StatusChangeModal', () => {
  it('should render modal with current status label', () => {
    renderModal()

    expect(screen.getByText('Cambiar estado del documento')).toBeInTheDocument()
    expect(screen.getByText('En revisión')).toBeInTheDocument()
  })

  it('should allow selecting a new status', async () => {
    const user = userEvent.setup()
    renderModal()

    const select = screen.getByRole('combobox')
    await user.selectOptions(select, 'approved')

    expect(select).toHaveValue('approved')
  })

  it('should show error when no status is selected and confirm is clicked', async () => {
    const user = userEvent.setup()
    renderModal()

    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    expect(screen.getByText('Selecciona un estado')).toBeInTheDocument()
  })

  it('should show rejection comment field when rejected is selected', async () => {
    const user = userEvent.setup()
    renderModal()

    await user.selectOptions(screen.getByRole('combobox'), 'rejected')

    expect(screen.getByPlaceholderText('Explica la razón del rechazo...')).toBeInTheDocument()
  })

  it('should show error when rejecting without a comment', async () => {
    const user = userEvent.setup()
    renderModal()

    await user.selectOptions(screen.getByRole('combobox'), 'rejected')
    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    expect(screen.getByText('El comentario de rechazo es obligatorio')).toBeInTheDocument()
  })

  it('should call onSuccess and onClose on successful status change', async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn().mockResolvedValue(undefined)
    const onClose = vi.fn()
    renderModal({ onSuccess, onClose })

    await user.selectOptions(screen.getByRole('combobox'), 'approved')
    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('approved', null)
    })
    expect(onClose).toHaveBeenCalled()
  })

  it('should send comment when rejecting successfully', async () => {
    const user = userEvent.setup()
    const comment = faker.lorem.sentence()
    const onSuccess = vi.fn().mockResolvedValue(undefined)
    const onClose = vi.fn()
    renderModal({ onSuccess, onClose })

    await user.selectOptions(screen.getByRole('combobox'), 'rejected')
    await user.type(screen.getByPlaceholderText('Explica la razón del rechazo...'), comment)
    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith('rejected', comment)
    })
    expect(onClose).toHaveBeenCalled()
  })

  it('should display error message when API call fails', async () => {
    const user = userEvent.setup()
    const detail = faker.lorem.sentence()
    const onSuccess = vi.fn().mockRejectedValue({ response: { data: { detail } } })
    renderModal({ onSuccess })

    await user.selectOptions(screen.getByRole('combobox'), 'approved')
    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    await waitFor(() => {
      expect(screen.getByText(detail)).toBeInTheDocument()
    })
  })

  it('should display fallback error when API error has no detail', async () => {
    const user = userEvent.setup()
    const onSuccess = vi.fn().mockRejectedValue(new Error('network'))
    renderModal({ onSuccess })

    await user.selectOptions(screen.getByRole('combobox'), 'approved')
    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))

    await waitFor(() => {
      expect(screen.getByText('Error al cambiar estado')).toBeInTheDocument()
    })
  })

  it('should clear error when selecting a new status', async () => {
    const user = userEvent.setup()
    renderModal()

    await user.click(screen.getByRole('button', { name: 'Cambiar estado' }))
    expect(screen.getByText('Selecciona un estado')).toBeInTheDocument()

    await user.selectOptions(screen.getByRole('combobox'), 'approved')
    expect(screen.queryByText('Selecciona un estado')).not.toBeInTheDocument()
  })

  it('should handle document with unknown status (no transitions)', () => {
    renderModal({ document: { status: 'unknown_status_xyz' } })

    expect(screen.getByText('Cambiar estado del documento')).toBeInTheDocument()
    const select = screen.getByRole('combobox')
    expect(select.querySelectorAll('option')).toHaveLength(1)
  })
})
