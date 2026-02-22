import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DocumentCreatePage from './DocumentCreatePage'
import { faker } from '../test/helpers'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

vi.mock('../api/documents', () => ({
  documentsApi: {
    create: vi.fn(),
  },
}))

import { documentsApi } from '../api/documents'

function getControl(labelText) {
  const label = screen.getByText(labelText, { exact: false, selector: 'label' })
  const wrapper = label.parentElement
  return wrapper.querySelector('select, input, textarea')
}

function renderPage() {
  return render(
    <MemoryRouter>
      <DocumentCreatePage />
    </MemoryRouter>
  )
}

function fillAndSubmit() {
  fireEvent.change(getControl('Tipo de documento'), { target: { value: 'invoice' } })
  fireEvent.change(getControl('Monto'), { target: { value: '5000' } })
  fireEvent.change(getControl('Creado por'), { target: { value: 'user@test.com' } })
  fireEvent.change(getControl('Cliente'), { target: { value: 'ClientX' } })
  fireEvent.change(getControl('Email'), { target: { value: 'cx@test.com' } })
  fireEvent.click(screen.getByRole('button', { name: 'Crear documento' }))
}

describe('DocumentCreatePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', () => {
    renderPage()
    expect(screen.getByText('Nuevo Documento')).toBeInTheDocument()
  })

  it('renders the description text', () => {
    renderPage()
    expect(
      screen.getByText('Completa los datos del documento para registrarlo en el sistema.')
    ).toBeInTheDocument()
  })

  it('renders a back link to /documents', () => {
    renderPage()
    const link = screen.getByText('← Volver a documentos')
    expect(link.closest('a')).toHaveAttribute('href', '/documents')
  })

  it('renders the document form with "Crear documento" submit label', () => {
    renderPage()
    expect(screen.getByRole('button', { name: 'Crear documento' })).toBeInTheDocument()
  })

  it('navigates to document detail on successful submit', async () => {
    const docId = faker.number.int({ min: 1, max: 9999 })
    documentsApi.create.mockResolvedValueOnce({ data: { id: docId } })

    renderPage()
    fillAndSubmit()

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(`/documents/${docId}`)
    })
  })

  it('shows error message on API failure with detail', async () => {
    const errorMsg = faker.lorem.sentence()
    documentsApi.create.mockRejectedValueOnce({
      response: { data: { detail: errorMsg } },
    })

    renderPage()
    fillAndSubmit()

    await waitFor(() => {
      expect(screen.getByText(errorMsg)).toBeInTheDocument()
    })
  })

  it('shows default error message when API error has no detail', async () => {
    documentsApi.create.mockRejectedValueOnce(new Error('Network Error'))

    renderPage()
    fillAndSubmit()

    await waitFor(() => {
      expect(screen.getByText('Error al crear el documento')).toBeInTheDocument()
    })
  })

  it('disables submit button while loading', async () => {
    let resolvePromise
    documentsApi.create.mockReturnValueOnce(
      new Promise((resolve) => {
        resolvePromise = resolve
      })
    )

    renderPage()
    fillAndSubmit()

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Guardando...' })).toBeDisabled()
    })

    resolvePromise({ data: { id: 1 } })
  })

  it('clears error before a new submit', async () => {
    const errorMsg = faker.lorem.sentence()
    documentsApi.create.mockRejectedValueOnce({
      response: { data: { detail: errorMsg } },
    })

    renderPage()
    fillAndSubmit()

    await waitFor(() => {
      expect(screen.getByText(errorMsg)).toBeInTheDocument()
    })

    documentsApi.create.mockResolvedValueOnce({ data: { id: 1 } })
    fillAndSubmit()

    await waitFor(() => {
      expect(screen.queryByText(errorMsg)).not.toBeInTheDocument()
    })
  })
})
