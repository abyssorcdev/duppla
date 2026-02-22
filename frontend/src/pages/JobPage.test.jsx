import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { faker, makeJob } from '../test/helpers'

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useParams: vi.fn() }
})

vi.mock('../hooks/useJobPolling', () => ({
  default: vi.fn(),
}))

import JobPage from './JobPage'
import { useParams } from 'react-router-dom'
import useJobPolling from '../hooks/useJobPolling'

function renderPage() {
  return render(
    <MemoryRouter>
      <JobPage />
    </MemoryRouter>,
  )
}

describe('JobPage', () => {
  const jobId = faker.string.uuid()

  beforeEach(() => {
    vi.clearAllMocks()
    useParams.mockReturnValue({ jobId })
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('shows loading spinner while loading', () => {
    useJobPolling.mockReturnValue({ job: null, loading: true, error: null })
    renderPage()
    expect(screen.getByText('Consultando job...')).toBeInTheDocument()
  })

  it('shows error state', () => {
    const errorMsg = faker.lorem.sentence()
    useJobPolling.mockReturnValue({ job: null, loading: false, error: errorMsg })
    renderPage()
    expect(screen.getByText(errorMsg)).toBeInTheDocument()
  })

  it('returns null when job is null and not loading/error', () => {
    useJobPolling.mockReturnValue({ job: null, loading: false, error: null })
    const { container } = renderPage()
    expect(container.innerHTML).toBe('')
  })

  it('passes jobId from useParams to useJobPolling', () => {
    useJobPolling.mockReturnValue({ job: null, loading: true, error: null })
    renderPage()
    expect(useJobPolling).toHaveBeenCalledWith(jobId)
  })

  it('renders header with job_id and status badge', () => {
    const job = makeJob({ job_id: jobId, status: 'completed', result: null })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('Job de procesamiento')).toBeInTheDocument()
    expect(screen.getByText(jobId)).toBeInTheDocument()
    expect(screen.getAllByText('Completado').length).toBeGreaterThanOrEqual(1)
  })

  it('shows ProcessingView for pending job', () => {
    const job = makeJob({ job_id: jobId, status: 'pending', result: { total: 5 } })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText(/Procesando documentos/)).toBeInTheDocument()
    expect(screen.getByText('5 documentos en cola')).toBeInTheDocument()
  })

  it('shows ProcessingView for processing job', () => {
    const job = makeJob({ job_id: jobId, status: 'processing', result: null })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText(/Procesando documentos/)).toBeInTheDocument()
    expect(screen.getByText('Calculando documentos...')).toBeInTheDocument()
  })

  it('shows elapsed timer text in ProcessingView', () => {
    const job = makeJob({ job_id: jobId, status: 'pending' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('00:00')).toBeInTheDocument()
    expect(screen.getByText('transcurrido')).toBeInTheDocument()
  })

  it('shows auto-update notice in ProcessingView', () => {
    const job = makeJob({ job_id: jobId, status: 'pending' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText(/Esta página se actualizará automáticamente/)).toBeInTheDocument()
  })

  it('shows ResultsView for completed job with progress bar and stats', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      completed_at: faker.date.recent().toISOString(),
      result: { total: 10, processed: 8, failed: 2 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('8 de 10 documentos procesados')).toBeInTheDocument()
    expect(screen.getByText('80%')).toBeInTheDocument()
    expect(screen.getByText('Total')).toBeInTheDocument()
    expect(screen.getByText('Exitosos')).toBeInTheDocument()
    expect(screen.getByText('Fallidos')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('shows failed job with error_message', () => {
    const errMsg = faker.lorem.sentence()
    const job = makeJob({
      job_id: jobId,
      status: 'failed',
      error_message: errMsg,
      result: { total: 3, processed: 1, failed: 2 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText(errMsg)).toBeInTheDocument()
    expect(screen.getByText(/Error:/)).toBeInTheDocument()
  })

  it('renders completed_at in ResultsView timeline', () => {
    const completedAt = '2025-07-15T12:00:00Z'
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      completed_at: completedAt,
      result: { total: 1, processed: 1, failed: 0 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('Iniciado')).toBeInTheDocument()
    expect(screen.getAllByText('Completado').length).toBeGreaterThanOrEqual(1)
  })

  it('shows "—" for completed_at when null in ResultsView', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'failed',
      completed_at: null,
      result: null,
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('—')).toBeInTheDocument()
  })

  it('does not render progress section when result is null', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'failed',
      result: null,
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.queryByText(/documentos procesados/)).not.toBeInTheDocument()
  })

  it('renders result details with success documents', () => {
    const docId = faker.number.int({ min: 1, max: 999 })
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: {
        total: 1,
        processed: 1,
        failed: 0,
        details: [{ document_id: docId, status: 'success' }],
      },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('Resultado por documento')).toBeInTheDocument()
    expect(screen.getByText(`#${docId}`)).toBeInTheDocument()
    expect(screen.getByText('Exitoso')).toBeInTheDocument()
    expect(document.querySelector(`a[href="/documents/${docId}"]`)).toBeInTheDocument()
  })

  it('renders result details with failed documents and error text', () => {
    const docId = faker.number.int({ min: 1, max: 999 })
    const errText = faker.lorem.words(3)
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: {
        total: 1,
        processed: 0,
        failed: 1,
        details: [{ document_id: docId, status: 'failed', error: errText }],
      },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText(`#${docId}`)).toBeInTheDocument()
    expect(screen.getByText('Fallido')).toBeInTheDocument()
    expect(screen.getByText(errText)).toBeInTheDocument()
  })

  it('does not render details section when details is empty', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: { total: 1, processed: 1, failed: 0, details: [] },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.queryByText('Resultado por documento')).not.toBeInTheDocument()
  })

  it('does not render details section when details is absent', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: { total: 1, processed: 1, failed: 0 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.queryByText('Resultado por documento')).not.toBeInTheDocument()
  })

  it('renders back link to documents', () => {
    const job = makeJob({ job_id: jobId, status: 'completed', result: null })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    const back = screen.getByText('Volver a documentos')
    expect(back.closest('a')).toHaveAttribute('href', '/documents')
  })

  it('falls back to job.status when JOB_STATUS_LABELS has no entry', () => {
    const job = makeJob({ job_id: jobId, status: 'exotic_status' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('exotic_status')).toBeInTheDocument()
  })

  it('uses red progress bar color for failed job', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'failed',
      result: { total: 5, processed: 2, failed: 3 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    const bar = document.querySelector('[style*="width"]')
    expect(bar.className).toContain('bg-red-500')
  })

  it('uses brand progress bar color for completed job', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: { total: 5, processed: 5, failed: 0 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    const bar = document.querySelector('[style*="width"]')
    expect(bar.className).toContain('bg-brand-700')
  })

  it('handles 0 total gracefully (0% progress)', () => {
    const job = makeJob({
      job_id: jobId,
      status: 'completed',
      result: { total: 0, processed: 0, failed: 0 },
    })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  it('advances AnimatedDots animation over time', async () => {
    const job = makeJob({ job_id: jobId, status: 'processing' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()

    await act(async () => {
      vi.advanceTimersByTime(500)
    })
    await act(async () => {
      vi.advanceTimersByTime(500)
    })
  })

  it('advances elapsed timer for active jobs', async () => {
    const job = makeJob({ job_id: jobId, status: 'pending' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    renderPage()
    expect(screen.getByText('00:00')).toBeInTheDocument()

    await act(async () => {
      vi.advanceTimersByTime(2000)
    })

    expect(screen.getByText('00:02')).toBeInTheDocument()
  })

  it('cleans up timers on unmount', async () => {
    const job = makeJob({ job_id: jobId, status: 'processing' })
    useJobPolling.mockReturnValue({ job, loading: false, error: null })

    const { unmount } = renderPage()

    await act(async () => {
      vi.advanceTimersByTime(500)
    })

    unmount()
  })
})
