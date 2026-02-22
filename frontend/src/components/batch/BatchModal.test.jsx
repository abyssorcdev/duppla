import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import BatchModal from './BatchModal'
import { faker } from '../../test/helpers'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}))

const mockProcessBatch = vi.fn()

vi.mock('../../api/documents', () => ({
  documentsApi: {
    processBatch: (...args) => mockProcessBatch(...args),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

function renderModal(overrides = {}) {
  const documentIds = overrides.documentIds ?? [
    faker.number.int({ min: 1, max: 999 }),
    faker.number.int({ min: 1, max: 999 }),
    faker.number.int({ min: 1, max: 999 }),
  ]
  const onClose = vi.fn()
  const onSuccess = vi.fn()

  const utils = render(
    <BatchModal
      documentIds={documentIds}
      onClose={overrides.onClose ?? onClose}
      onSuccess={overrides.onSuccess ?? onSuccess}
    />,
  )

  return { ...utils, documentIds, onClose, onSuccess }
}

describe('BatchModal', () => {
  it('should render document count', () => {
    const { documentIds } = renderModal()

    expect(screen.getByText(`${documentIds.length} documentos`)).toBeInTheDocument()
  })

  it('should display all selected document IDs', () => {
    const { documentIds } = renderModal()

    documentIds.forEach((id) => {
      expect(screen.getByText(`#${id}`)).toBeInTheDocument()
    })
  })

  it('should call processBatch API on confirm', async () => {
    const user = userEvent.setup()
    const jobId = faker.string.uuid()
    mockProcessBatch.mockResolvedValue({ data: { job_id: jobId } })
    const { documentIds, onSuccess, onClose } = renderModal()

    await user.click(screen.getByRole('button', { name: 'Iniciar procesamiento' }))

    await waitFor(() => {
      expect(mockProcessBatch).toHaveBeenCalledWith(documentIds)
    })
    expect(onSuccess).toHaveBeenCalled()
    expect(onClose).toHaveBeenCalled()
  })

  it('should navigate to job page on success', async () => {
    const user = userEvent.setup()
    const jobId = faker.string.uuid()
    mockProcessBatch.mockResolvedValue({ data: { job_id: jobId } })
    renderModal()

    await user.click(screen.getByRole('button', { name: 'Iniciar procesamiento' }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(`/jobs/${jobId}`)
    })
  })

  it('should show error message on API failure', async () => {
    const user = userEvent.setup()
    const detail = faker.lorem.sentence()
    mockProcessBatch.mockRejectedValue({ response: { data: { detail } } })
    renderModal()

    await user.click(screen.getByRole('button', { name: 'Iniciar procesamiento' }))

    await waitFor(() => {
      expect(screen.getByText(detail)).toBeInTheDocument()
    })
  })

  it('should show fallback error when API error has no detail', async () => {
    const user = userEvent.setup()
    mockProcessBatch.mockRejectedValue(new Error('network'))
    renderModal()

    await user.click(screen.getByRole('button', { name: 'Iniciar procesamiento' }))

    await waitFor(() => {
      expect(screen.getByText('Error al iniciar el procesamiento')).toBeInTheDocument()
    })
  })

  it('should call onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup()
    const { onClose } = renderModal()

    await user.click(screen.getByRole('button', { name: 'Cancelar' }))

    expect(onClose).toHaveBeenCalled()
  })
})
