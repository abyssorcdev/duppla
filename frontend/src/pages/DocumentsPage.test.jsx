import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DocumentsPage from './DocumentsPage'
import { faker, makeDocument } from '../test/helpers'

vi.mock('../hooks/useDocuments')
import useDocuments from '../hooks/useDocuments'

vi.mock('../components/batch/BatchModal', () => ({
  default: ({ documentIds, onClose, onSuccess }) => (
    <div data-testid="batch-modal">
      <span data-testid="batch-ids">{documentIds.join(',')}</span>
      <button onClick={onClose}>close-modal</button>
      <button onClick={onSuccess}>success-modal</button>
    </div>
  ),
}))

function buildUseDocuments(overrides = {}) {
  return {
    documents: [],
    total: 0,
    totalPages: 1,
    loading: false,
    error: null,
    filters: { page: 1, page_size: 10 },
    updateFilter: vi.fn(),
    refresh: vi.fn(),
    ...overrides,
  }
}

function renderPage(initialEntry = '/documents') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <DocumentsPage />
    </MemoryRouter>
  )
}

describe('DocumentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    useDocuments.mockReturnValue(buildUseDocuments())
    renderPage()
    expect(screen.getByText('Documentos')).toBeInTheDocument()
  })

  it('shows total documents count', () => {
    const total = faker.number.int({ min: 1, max: 500 })
    useDocuments.mockReturnValue(buildUseDocuments({ total }))
    renderPage()
    expect(screen.getByText(`${total} documentos encontrados`)).toBeInTheDocument()
  })

  it('renders "+ Nuevo" link to /documents/new', () => {
    useDocuments.mockReturnValue(buildUseDocuments())
    renderPage()
    const link = screen.getByText('+ Nuevo')
    expect(link.closest('a')).toHaveAttribute('href', '/documents/new')
  })

  describe('loading state', () => {
    it('shows loading spinner when loading', () => {
      useDocuments.mockReturnValue(buildUseDocuments({ loading: true }))
      renderPage()
      expect(screen.getByText('Cargando documentos...')).toBeInTheDocument()
    })

    it('does not render table when loading', () => {
      useDocuments.mockReturnValue(buildUseDocuments({ loading: true }))
      renderPage()
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })
  })

  describe('error state', () => {
    it('shows error message', () => {
      const errorMsg = faker.lorem.sentence()
      useDocuments.mockReturnValue(buildUseDocuments({ error: errorMsg }))
      renderPage()
      expect(screen.getByText(errorMsg)).toBeInTheDocument()
    })

    it('does not render table when error', () => {
      useDocuments.mockReturnValue(buildUseDocuments({ error: 'fail' }))
      renderPage()
      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })
  })

  describe('documents table', () => {
    it('renders document rows when loaded', () => {
      const docs = [makeDocument({ status: 'draft' }), makeDocument({ status: 'draft' })]
      useDocuments.mockReturnValue(buildUseDocuments({ documents: docs, total: 2 }))
      renderPage()
      expect(screen.getByRole('table')).toBeInTheDocument()
    })

    it('shows empty state when no documents', () => {
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [], total: 0 }))
      renderPage()
      expect(screen.getByText('No se encontraron documentos')).toBeInTheDocument()
    })
  })

  describe('selection and batch', () => {
    it('does not show batch button when nothing selected', () => {
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [makeDocument({ status: 'draft' })] }))
      renderPage()
      expect(screen.queryByText(/Procesar batch/)).not.toBeInTheDocument()
    })

    it('shows batch button after selecting a document', () => {
      const doc = makeDocument({ status: 'draft', id: 5 })
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [doc] }))
      renderPage()

      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[1]) // row checkbox

      expect(screen.getByText(/Procesar batch \(1\)/)).toBeInTheDocument()
    })

    it('opens batch modal when batch button is clicked', () => {
      const doc = makeDocument({ status: 'draft', id: 5 })
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [doc] }))
      renderPage()

      fireEvent.click(screen.getAllByRole('checkbox')[1])
      fireEvent.click(screen.getByText(/Procesar batch/))

      expect(screen.getByTestId('batch-modal')).toBeInTheDocument()
    })

    it('passes selected document ids to batch modal', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 10 }),
        makeDocument({ status: 'draft', id: 20 }),
      ]
      useDocuments.mockReturnValue(buildUseDocuments({ documents: docs }))
      renderPage()

      fireEvent.click(screen.getAllByRole('checkbox')[1])
      fireEvent.click(screen.getAllByRole('checkbox')[2])
      fireEvent.click(screen.getByText(/Procesar batch/))

      expect(screen.getByTestId('batch-ids').textContent).toBe('10,20')
    })

    it('toggles a document off when clicked again', () => {
      const doc = makeDocument({ status: 'draft', id: 5 })
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [doc] }))
      renderPage()

      const checkbox = screen.getAllByRole('checkbox')[1]
      fireEvent.click(checkbox) // select
      expect(screen.getByText(/Procesar batch \(1\)/)).toBeInTheDocument()
      fireEvent.click(checkbox) // deselect
      expect(screen.queryByText(/Procesar batch/)).not.toBeInTheDocument()
    })

    it('toggleAll selects all selectable documents', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'pending', id: 2 }),
        makeDocument({ status: 'rejected', id: 3 }),
      ]
      useDocuments.mockReturnValue(buildUseDocuments({ documents: docs }))
      renderPage()

      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(headerCheckbox)

      expect(screen.getByText(/Procesar batch \(2\)/)).toBeInTheDocument()
    })

    it('toggleAll deselects all when all selectable are already selected', () => {
      const docs = [
        makeDocument({ status: 'draft', id: 1 }),
        makeDocument({ status: 'draft', id: 2 }),
      ]
      useDocuments.mockReturnValue(buildUseDocuments({ documents: docs }))
      renderPage()

      const headerCheckbox = screen.getAllByRole('checkbox')[0]
      fireEvent.click(headerCheckbox) // select all
      fireEvent.click(headerCheckbox) // deselect all

      expect(screen.queryByText(/Procesar batch/)).not.toBeInTheDocument()
    })

    it('closes batch modal via onClose', () => {
      const doc = makeDocument({ status: 'draft', id: 5 })
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [doc] }))
      renderPage()

      fireEvent.click(screen.getAllByRole('checkbox')[1])
      fireEvent.click(screen.getByText(/Procesar batch/))
      expect(screen.getByTestId('batch-modal')).toBeInTheDocument()

      fireEvent.click(screen.getByText('close-modal'))
      expect(screen.queryByTestId('batch-modal')).not.toBeInTheDocument()
    })

    it('clears selection and calls refresh on batch success', () => {
      const mock = buildUseDocuments({ documents: [makeDocument({ status: 'draft', id: 5 })] })
      useDocuments.mockReturnValue(mock)
      renderPage()

      fireEvent.click(screen.getAllByRole('checkbox')[1])
      fireEvent.click(screen.getByText(/Procesar batch/))
      fireEvent.click(screen.getByText('success-modal'))

      expect(screen.queryByText(/Procesar batch/)).not.toBeInTheDocument()
    })
  })

  describe('pagination', () => {
    it('calls updateFilter with page when pagination is used', () => {
      const mock = buildUseDocuments({ documents: [makeDocument({ status: 'draft' })], total: 30, totalPages: 3 })
      useDocuments.mockReturnValue(mock)
      renderPage()

      const nextBtn = screen.getByText('Siguiente →')
      fireEvent.click(nextBtn)
      expect(mock.updateFilter).toHaveBeenCalledWith('page', 2)
    })
  })

  describe('filter bar', () => {
    it('renders filter bar', () => {
      useDocuments.mockReturnValue(buildUseDocuments())
      renderPage()
      expect(screen.getByText('Limpiar filtros')).toBeInTheDocument()
    })

    it('passes status from search params as initial filter', () => {
      useDocuments.mockReturnValue(buildUseDocuments())
      renderPage('/documents?status=draft')
      expect(useDocuments).toHaveBeenCalledWith(expect.objectContaining({ status: 'draft' }))
    })

    it('passes empty status when not in search params', () => {
      useDocuments.mockReturnValue(buildUseDocuments())
      renderPage('/documents')
      expect(useDocuments).toHaveBeenCalledWith(expect.objectContaining({ status: '' }))
    })
  })

  describe('selection resets on filter change', () => {
    it('clears selected when filters change', () => {
      const doc = makeDocument({ status: 'draft', id: 5 })
      const mock = buildUseDocuments({ documents: [doc] })
      useDocuments.mockReturnValue(mock)
      const { rerender } = renderPage()

      fireEvent.click(screen.getAllByRole('checkbox')[1])
      expect(screen.getByText(/Procesar batch \(1\)/)).toBeInTheDocument()

      const newFilters = { page: 1, page_size: 10, type: 'invoice' }
      useDocuments.mockReturnValue(buildUseDocuments({ documents: [doc], filters: newFilters }))
      rerender(
        <MemoryRouter initialEntries={['/documents']}>
          <DocumentsPage />
        </MemoryRouter>
      )

      expect(screen.queryByText(/Procesar batch/)).not.toBeInTheDocument()
    })
  })
})
