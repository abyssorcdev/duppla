import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { faker, makeJob } from '../test/helpers'

vi.mock('../hooks/useJobs', () => ({
  default: vi.fn(),
}))

vi.mock('../components/common/LoadingSpinner', () => ({
  default: ({ text }) => <div data-testid="spinner">{text}</div>,
}))

vi.mock('../components/common/Pagination', () => ({
  default: ({ page, totalPages, onPageChange }) => (
    <div data-testid="pagination">
      <span>Page {page} of {totalPages}</span>
      <button onClick={() => onPageChange(page + 1)}>next</button>
    </div>
  ),
}))

import JobsPage from './JobsPage'
import useJobs from '../hooks/useJobs'

function renderPage() {
  return render(
    <MemoryRouter>
      <JobsPage />
    </MemoryRouter>,
  )
}

function mockHook(overrides = {}) {
  const value = {
    jobs: [],
    total: 0,
    totalPages: 0,
    loading: false,
    error: null,
    filters: { page: 1, status: '' },
    updateFilter: vi.fn(),
    ...overrides,
  }
  useJobs.mockReturnValue(value)
  return value
}

describe('JobsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading spinner while loading', () => {
    mockHook({ loading: true })
    renderPage()
    expect(screen.getByTestId('spinner')).toHaveTextContent('Cargando jobs...')
  })

  it('shows error state', () => {
    const errorMsg = faker.lorem.sentence()
    mockHook({ error: errorMsg })
    renderPage()
    expect(screen.getByText(errorMsg)).toBeInTheDocument()
  })

  it('shows empty state when no jobs', () => {
    mockHook({ jobs: [] })
    renderPage()
    expect(screen.getByText('No hay jobs con este estado')).toBeInTheDocument()
  })

  it('renders header with total count', () => {
    const total = faker.number.int({ min: 1, max: 100 })
    mockHook({ total })
    renderPage()
    expect(screen.getByText('Jobs de procesamiento')).toBeInTheDocument()
    expect(screen.getByText(`${total} jobs en total`)).toBeInTheDocument()
  })

  it('renders job rows with job_id, status badge', () => {
    const jobs = [
      makeJob({ status: 'completed', result: { total: 5, processed: 3 } }),
      makeJob({ status: 'pending' }),
    ]
    mockHook({ jobs, total: 2, totalPages: 1 })

    renderPage()
    for (const job of jobs) {
      expect(screen.getByText(job.job_id)).toBeInTheDocument()
    }
    expect(screen.getAllByText('Completado').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1)
  })

  it('renders all status filter buttons', () => {
    mockHook()
    renderPage()

    expect(screen.getByText('Todos')).toBeInTheDocument()
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
    expect(screen.getByText('Procesando')).toBeInTheDocument()
    expect(screen.getByText('Completado')).toBeInTheDocument()
    expect(screen.getByText('Fallido')).toBeInTheDocument()
  })

  it('calls updateFilter when status filter is clicked', () => {
    const { updateFilter } = mockHook()
    renderPage()

    fireEvent.click(screen.getByText('Completado'))
    expect(updateFilter).toHaveBeenCalledWith('status', 'completed')
  })

  it('highlights active filter button', () => {
    mockHook({ filters: { page: 1, status: 'failed' } })
    renderPage()
    const failedBtn = screen.getByText('Fallido')
    expect(failedBtn.className).toContain('bg-brand-700')
  })

  it('renders pagination when totalPages > 1', () => {
    mockHook({ jobs: [makeJob()], total: 20, totalPages: 2 })
    renderPage()
    expect(screen.getByTestId('pagination')).toBeInTheDocument()
  })

  it('pagination calls updateFilter with page', () => {
    const { updateFilter } = mockHook({ jobs: [makeJob()], total: 20, totalPages: 2 })
    renderPage()
    fireEvent.click(screen.getByText('next'))
    expect(updateFilter).toHaveBeenCalledWith('page', 2)
  })

  it('renders completed_at date when present', () => {
    const completedAt = '2025-08-01T14:30:00Z'
    const job = makeJob({ status: 'completed', completed_at: completedAt })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    const completedTexts = screen.getAllByText(/Completado/)
    expect(completedTexts.length).toBeGreaterThanOrEqual(2)
  })

  it('hides completed_at when absent', () => {
    const job = makeJob({ status: 'pending', completed_at: null })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    const jobRow = document.querySelector(`a[href="/jobs/${job.job_id}"]`)
    expect(jobRow.textContent).not.toContain('Completado')
  })

  it('renders result stats (processed/total) when available', () => {
    const job = makeJob({ status: 'completed', result: { total: 10, processed: 7 } })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('7')).toBeInTheDocument()
  })

  it('renders "—" for total and processed when result is null', () => {
    const job = makeJob({ status: 'pending', result: null })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    const dashes = screen.getAllByText('—')
    expect(dashes.length).toBeGreaterThanOrEqual(2)
  })

  it('links job rows to /jobs/:jobId', () => {
    const job = makeJob()
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    expect(document.querySelector(`a[href="/jobs/${job.job_id}"]`)).toBeInTheDocument()
  })

  it('falls back to job.status when JOB_STATUS_LABELS has no entry', () => {
    const job = makeJob({ status: 'custom_unknown' })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    expect(screen.getByText('custom_unknown')).toBeInTheDocument()
  })

  it('applies green color for processed > 0', () => {
    const job = makeJob({ status: 'completed', result: { total: 3, processed: 2 } })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    const processedEl = screen.getByText('2')
    expect(processedEl.className).toContain('text-green-600')
  })

  it('applies gray color for processed = 0 (number)', () => {
    const job = makeJob({ status: 'completed', result: { total: 3, processed: 0 } })
    mockHook({ jobs: [job], total: 1, totalPages: 1 })

    renderPage()
    const zeros = screen.getAllByText('0')
    const processedZero = zeros.find((el) => el.className.includes('text-gray-400'))
    expect(processedZero).toBeTruthy()
  })
})
