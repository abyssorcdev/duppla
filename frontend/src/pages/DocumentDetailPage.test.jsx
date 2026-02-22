import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { faker, makeDocument } from '../test/helpers'

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useParams: vi.fn() }
})

vi.mock('../api/documents', () => ({
  documentsApi: {
    get: vi.fn(),
    update: vi.fn(),
    changeStatus: vi.fn(),
  },
}))

vi.mock('../components/common/StatusBadge', () => ({
  default: ({ status }) => <span data-testid="status-badge">{status}</span>,
}))

vi.mock('../components/common/LoadingSpinner', () => ({
  default: ({ text }) => <div data-testid="spinner">{text}</div>,
}))

vi.mock('../components/documents/DocumentForm', () => ({
  default: ({ onSubmit, loading, submitLabel }) => (
    <form data-testid="document-form" onSubmit={(e) => { e.preventDefault(); onSubmit({ type: 'invoice', amount: 100, created_by: 'u1', metadata: {} }) }}>
      <button type="submit" disabled={loading}>{loading ? 'Guardando...' : submitLabel}</button>
    </form>
  ),
}))

vi.mock('../components/documents/StatusChangeModal', () => ({
  default: ({ document, onClose, onSuccess }) => (
    <div data-testid="status-modal">
      <span>Modal for {document.id}</span>
      <button onClick={() => onSuccess('approved', null)}>confirm</button>
      <button onClick={onClose}>close</button>
    </div>
  ),
}))

import DocumentDetailPage from './DocumentDetailPage'
import { useParams } from 'react-router-dom'
import { documentsApi } from '../api/documents'

function renderPage() {
  return render(
    <MemoryRouter>
      <DocumentDetailPage />
    </MemoryRouter>,
  )
}

describe('DocumentDetailPage', () => {
  const docId = faker.number.int({ min: 1, max: 9999 }).toString()

  beforeEach(() => {
    vi.clearAllMocks()
    useParams.mockReturnValue({ id: docId })
  })

  it('shows loading spinner while fetching', () => {
    documentsApi.get.mockReturnValue(new Promise(() => {}))
    renderPage()
    expect(screen.getByTestId('spinner')).toHaveTextContent('Cargando documento...')
  })

  it('shows error state when API fails', async () => {
    documentsApi.get.mockRejectedValueOnce(new Error('fail'))
    renderPage()
    expect(await screen.findByText('No se pudo cargar el documento')).toBeInTheDocument()
  })

  it('renders document details after loading', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'approved', amount: 50000 })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText(`Documento #${docId}`)).toBeInTheDocument()
    expect(screen.getByTestId('status-badge')).toHaveTextContent('approved')
    expect(screen.getByText(doc.created_by)).toBeInTheDocument()
  })

  it('shows edit button only for draft status', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Editar')).toBeInTheDocument()
  })

  it('hides edit button for non-draft status', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'approved' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Editar')).not.toBeInTheDocument()
  })

  it('shows "Cambiar estado" button when transitions available (draft -> pending)', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Cambiar estado')).toBeInTheDocument()
  })

  it('shows "Cambiar estado" button for pending status (pending -> approved/rejected)', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'pending' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Cambiar estado')).toBeInTheDocument()
  })

  it('hides "Cambiar estado" for approved (no transitions)', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'approved' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Cambiar estado')).not.toBeInTheDocument()
  })

  it('hides "Cambiar estado" for rejected (no transitions)', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'rejected' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Cambiar estado')).not.toBeInTheDocument()
  })

  it('enters edit mode when Editar is clicked', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    fireEvent.click(await screen.findByText('Editar'))
    expect(screen.getByTestId('document-form')).toBeInTheDocument()
    expect(screen.getByText('Editar documento')).toBeInTheDocument()
    expect(screen.queryByText('Editar')).not.toBeInTheDocument()
    expect(screen.queryByText('Cambiar estado')).not.toBeInTheDocument()
  })

  it('cancel button exits edit mode', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    fireEvent.click(await screen.findByText('Editar'))
    fireEvent.click(screen.getByText('Cancelar'))
    expect(screen.queryByTestId('document-form')).not.toBeInTheDocument()
    expect(screen.getByText('Editar')).toBeInTheDocument()
  })

  it('successful update exits edit mode and refreshes', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    const updated = { ...doc, amount: 99999 }
    documentsApi.get.mockResolvedValueOnce({ data: doc })
    documentsApi.update.mockResolvedValueOnce({ data: updated })

    renderPage()
    fireEvent.click(await screen.findByText('Editar'))
    fireEvent.click(screen.getByText('Guardar cambios'))

    await waitFor(() => {
      expect(screen.queryByTestId('document-form')).not.toBeInTheDocument()
    })
    expect(documentsApi.update).toHaveBeenCalledWith(
      docId,
      expect.objectContaining({ user_id: 'u1' }),
    )
  })

  it('update error shows error message', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })
    documentsApi.update.mockRejectedValueOnce({
      response: { data: { detail: 'Monto inválido' } },
    })

    renderPage()
    fireEvent.click(await screen.findByText('Editar'))
    fireEvent.click(screen.getByText('Guardar cambios'))

    expect(await screen.findByText('Monto inválido')).toBeInTheDocument()
    expect(screen.getByTestId('document-form')).toBeInTheDocument()
  })

  it('update error falls back to generic message', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })
    documentsApi.update.mockRejectedValueOnce(new Error('boom'))

    renderPage()
    fireEvent.click(await screen.findByText('Editar'))
    fireEvent.click(screen.getByText('Guardar cambios'))

    expect(await screen.findByText('Error al actualizar')).toBeInTheDocument()
  })

  it('opens status change modal when "Cambiar estado" is clicked', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    fireEvent.click(await screen.findByText('Cambiar estado'))
    expect(screen.getByTestId('status-modal')).toBeInTheDocument()
    expect(screen.getByText(`Modal for ${doc.id}`)).toBeInTheDocument()
  })

  it('closes status change modal on close', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    fireEvent.click(await screen.findByText('Cambiar estado'))
    fireEvent.click(screen.getByText('close'))
    expect(screen.queryByTestId('status-modal')).not.toBeInTheDocument()
  })

  it('status change calls changeStatus and reloads', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })
    documentsApi.changeStatus.mockResolvedValueOnce({})
    const reloaded = { ...doc, status: 'approved' }
    documentsApi.get.mockResolvedValueOnce({ data: reloaded })

    renderPage()
    fireEvent.click(await screen.findByText('Cambiar estado'))
    fireEvent.click(screen.getByText('confirm'))

    await waitFor(() => {
      expect(documentsApi.changeStatus).toHaveBeenCalledWith(docId, 'approved', null)
    })
  })

  it('renders metadata with client, email, reference', async () => {
    const meta = {
      client: faker.company.name(),
      email: faker.internet.email(),
      reference: faker.string.alphanumeric(10),
    }
    const doc = makeDocument({ id: Number(docId), status: 'approved', metadata: meta })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText(meta.client)).toBeInTheDocument()
    expect(screen.getByText(meta.email)).toBeInTheDocument()
    expect(screen.getByText(meta.reference)).toBeInTheDocument()
  })

  it('renders rejection_comment metadata', async () => {
    const comment = faker.lorem.sentence()
    const rejectedBy = faker.internet.email()
    const doc = makeDocument({
      id: Number(docId),
      status: 'rejected',
      metadata: { rejection_comment: comment, rejected_by: rejectedBy },
    })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText(comment)).toBeInTheDocument()
    expect(screen.getByText(rejectedBy)).toBeInTheDocument()
    expect(screen.getByText('Rechazo manual')).toBeInTheDocument()
  })

  it('renders processed_by_job metadata with link', async () => {
    const jobId = faker.string.uuid()
    const doc = makeDocument({
      id: Number(docId),
      status: 'approved',
      metadata: { processed_by_job: jobId },
    })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText(jobId)).toBeInTheDocument()
    expect(screen.getByText('Procesamiento automático')).toBeInTheDocument()
    expect(document.querySelector(`a[href="/jobs/${jobId}"]`)).toBeInTheDocument()
  })

  it('renders rejection_reason alongside processed_by_job', async () => {
    const reason = faker.lorem.sentence()
    const doc = makeDocument({
      id: Number(docId),
      status: 'rejected',
      metadata: { processed_by_job: faker.string.uuid(), rejection_reason: reason },
    })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText(reason)).toBeInTheDocument()
  })

  it('renders empty metadata state', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft', metadata: {} })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Sin metadata')).toBeInTheDocument()
  })

  it('renders null metadata as empty', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft', metadata: null })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Sin metadata')).toBeInTheDocument()
  })

  it('renders full JSON in metadata section', async () => {
    const meta = { client: 'Acme', email: 'a@b.com' }
    const doc = makeDocument({ id: Number(docId), status: 'approved', metadata: meta })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('JSON completo')).toBeInTheDocument()
  })

  it('renders updated_at field when present', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft', updated_at: '2025-06-15T10:30:00Z' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    expect(await screen.findByText('Actualizado el')).toBeInTheDocument()
  })

  it('hides updated_at field when absent', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft', updated_at: null })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Actualizado el')).not.toBeInTheDocument()
  })

  it('renders back link to documents list', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    const back = await screen.findByText(/Volver a documentos/)
    expect(back.closest('a')).toHaveAttribute('href', '/documents')
  })

  it('falls back to doc.type when TYPE_LABELS has no entry', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'draft', type: 'unknown_type' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    const matches = await screen.findAllByText('unknown_type')
    expect(matches.length).toBeGreaterThanOrEqual(1)
  })

  it('hides status change button when doc status has no valid transitions', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'approved' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Cambiar estado')).not.toBeInTheDocument()
  })

  it('handles unknown status gracefully for transitions fallback', async () => {
    const doc = makeDocument({ id: Number(docId), status: 'unknown_xyz' })
    documentsApi.get.mockResolvedValueOnce({ data: doc })

    renderPage()
    await screen.findByText(`Documento #${docId}`)
    expect(screen.queryByText('Cambiar estado')).not.toBeInTheDocument()
  })
})
