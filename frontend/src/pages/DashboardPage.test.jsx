import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { faker } from '../test/helpers'
import { makeDocument, makeJob } from '../test/helpers'

vi.mock('../api/documents', () => ({
  documentsApi: {
    list: vi.fn(),
  },
}))

vi.mock('../api/jobs', () => ({
  jobsApi: {
    list: vi.fn(),
  },
}))

vi.mock('../components/common/LoadingSpinner', () => ({
  default: ({ text }) => <div data-testid="spinner">{text}</div>,
}))

import DashboardPage from './DashboardPage'
import { documentsApi } from '../api/documents'
import { jobsApi } from '../api/jobs'

function renderPage() {
  return render(
    <MemoryRouter>
      <DashboardPage />
    </MemoryRouter>,
  )
}

function mockSuccessfulLoad({ docs = [], jobs = [], counts = {} } = {}) {
  const draftCount = counts.draft ?? faker.number.int({ min: 0, max: 50 })
  const pendingCount = counts.pending ?? faker.number.int({ min: 0, max: 50 })
  const approvedCount = counts.approved ?? faker.number.int({ min: 0, max: 50 })
  const rejectedCount = counts.rejected ?? faker.number.int({ min: 0, max: 50 })

  jobsApi.list.mockResolvedValueOnce({ data: { items: jobs } })
  documentsApi.list
    .mockResolvedValueOnce({ data: { total: draftCount } })
    .mockResolvedValueOnce({ data: { total: pendingCount } })
    .mockResolvedValueOnce({ data: { total: approvedCount } })
    .mockResolvedValueOnce({ data: { total: rejectedCount } })
    .mockResolvedValueOnce({ data: { items: docs } })

  return { draftCount, pendingCount, approvedCount, rejectedCount }
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner while fetching data', () => {
    jobsApi.list.mockReturnValue(new Promise(() => {}))
    documentsApi.list.mockReturnValue(new Promise(() => {}))

    renderPage()
    expect(screen.getByTestId('spinner')).toHaveTextContent('Cargando dashboard...')
  })

  it('renders stats cards with correct counts after loading', async () => {
    const { draftCount, pendingCount, approvedCount, rejectedCount } =
      mockSuccessfulLoad()

    renderPage()

    const total = draftCount + pendingCount + approvedCount + rejectedCount
    expect(await screen.findByText(String(total))).toBeInTheDocument()
    expect(screen.getByText(String(draftCount))).toBeInTheDocument()
    expect(screen.getByText(String(pendingCount))).toBeInTheDocument()
    expect(screen.getByText(String(approvedCount))).toBeInTheDocument()
    expect(screen.getByText(String(rejectedCount))).toBeInTheDocument()
  })

  it('renders recent documents', async () => {
    const docs = [makeDocument(), makeDocument()]
    mockSuccessfulLoad({ docs })

    renderPage()

    for (const doc of docs) {
      expect(await screen.findByText(new RegExp(`#${doc.id}`))).toBeInTheDocument()
    }
  })

  it('renders recent jobs', async () => {
    const jobs = [
      makeJob({ status: 'completed', result: { processed: 3, total: 5 } }),
      makeJob({ status: 'pending' }),
    ]
    mockSuccessfulLoad({ jobs })

    renderPage()

    for (const job of jobs) {
      expect(await screen.findByText(job.job_id)).toBeInTheDocument()
    }
    expect(screen.getByText('3/5 docs')).toBeInTheDocument()
  })

  it('shows empty state when there are no documents', async () => {
    mockSuccessfulLoad({ docs: [], counts: { draft: 0, pending: 0, approved: 0, rejected: 0 } })

    renderPage()
    expect(await screen.findByText(/No hay documentos aún/)).toBeInTheDocument()
    expect(screen.getByText('Crea el primero')).toBeInTheDocument()
  })

  it('shows empty state when there are no jobs', async () => {
    mockSuccessfulLoad({ jobs: [] })

    renderPage()
    expect(await screen.findByText(/No hay jobs ejecutados aún/)).toBeInTheDocument()
  })

  it('handles API error silently and stops loading', async () => {
    jobsApi.list.mockRejectedValueOnce(new Error('network'))
    documentsApi.list.mockRejectedValue(new Error('network'))

    renderPage()

    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
    expect(screen.queryByTestId('spinner')).not.toBeInTheDocument()
  })

  it('links to /documents from total card', async () => {
    mockSuccessfulLoad({ docs: [makeDocument()] })

    renderPage()
    const link = await screen.findByText('Ver todos los documentos')
    expect(link.closest('a')).toHaveAttribute('href', '/documents')
  })

  it('links to /documents?status=X from status cards', async () => {
    mockSuccessfulLoad({ docs: [makeDocument()] })

    renderPage()
    await screen.findByText('Dashboard')
    const statusLinks = ['draft', 'pending', 'approved', 'rejected']
    for (const status of statusLinks) {
      expect(document.querySelector(`a[href="/documents?status=${status}"]`)).toBeInTheDocument()
    }
  })

  it('links to /jobs from jobs section', async () => {
    mockSuccessfulLoad({ jobs: [makeJob()] })

    renderPage()
    const links = await screen.findAllByText('Ver todos')
    const jobsLink = links.find((el) => el.closest('a')?.getAttribute('href') === '/jobs')
    expect(jobsLink).toBeTruthy()
  })

  it('links to individual document pages', async () => {
    const doc = makeDocument({ id: 42 })
    mockSuccessfulLoad({ docs: [doc] })

    renderPage()
    await screen.findByText(/#42/)
    expect(document.querySelector('a[href="/documents/42"]')).toBeInTheDocument()
  })

  it('links to individual job pages', async () => {
    const job = makeJob()
    mockSuccessfulLoad({ jobs: [job] })

    renderPage()
    await screen.findByText(job.job_id)
    expect(document.querySelector(`a[href="/jobs/${job.job_id}"]`)).toBeInTheDocument()
  })

  it('renders job status labels and badges', async () => {
    const jobs = [
      makeJob({ status: 'completed' }),
      makeJob({ status: 'failed' }),
      makeJob({ status: 'processing' }),
      makeJob({ status: 'pending' }),
    ]
    mockSuccessfulLoad({ jobs })

    renderPage()
    expect(await screen.findByText('Completado')).toBeInTheDocument()
    expect(screen.getByText('Fallido')).toBeInTheDocument()
    expect(screen.getByText('Procesando')).toBeInTheDocument()
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
  })

  it('renders percentage bars when total > 0', async () => {
    mockSuccessfulLoad({ counts: { draft: 10, pending: 5, approved: 3, rejected: 2 } })

    renderPage()
    await screen.findByText('20')
    expect(screen.getByText('50% del total')).toBeInTheDocument()
  })

  it('does not render percentage bars when total is 0', async () => {
    mockSuccessfulLoad({
      docs: [],
      counts: { draft: 0, pending: 0, approved: 0, rejected: 0 },
    })

    renderPage()
    await screen.findAllByText('0')
    expect(screen.queryByText(/del total/)).not.toBeInTheDocument()
  })

  it('renders job without result stats gracefully', async () => {
    const job = makeJob({ status: 'pending', result: null })
    mockSuccessfulLoad({ jobs: [job] })

    renderPage()
    await screen.findByText(job.job_id)
    expect(screen.queryByText(/docs/)).not.toBeInTheDocument()
  })

  it('falls back to status value when JOB_STATUS_LABELS has no entry', async () => {
    const job = makeJob({ status: 'unknown_status' })
    mockSuccessfulLoad({ jobs: [job] })

    renderPage()
    expect(await screen.findByText('unknown_status')).toBeInTheDocument()
  })

  it('renders job result with null processed and total using ?? fallback', async () => {
    const job = makeJob({ status: 'completed', result: { processed: null, total: null } })
    mockSuccessfulLoad({ jobs: [job] })

    renderPage()
    await screen.findByText(job.job_id)
    expect(screen.getByText('0/0 docs')).toBeInTheDocument()
  })

  it('handles stats where a status key is missing (nullish coalescing)', async () => {
    jobsApi.list.mockResolvedValueOnce({ data: { items: [] } })
    documentsApi.list
      .mockResolvedValueOnce({ data: { total: 5 } })
      .mockResolvedValueOnce({ data: { total: 3 } })
      .mockResolvedValueOnce({ data: { total: undefined } })
      .mockResolvedValueOnce({ data: { total: null } })
      .mockResolvedValueOnce({ data: { items: [] } })

    renderPage()
    await screen.findByText('Dashboard')
  })
})
