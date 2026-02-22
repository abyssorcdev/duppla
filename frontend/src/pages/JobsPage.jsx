import { Link } from 'react-router-dom'
import useJobs from '../hooks/useJobs'
import Pagination from '../components/common/Pagination'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { formatDate } from '../utils/formatters'

const JOB_STATUS_STYLES = {
  pending:    'bg-gray-100 text-gray-600',
  processing: 'bg-blue-100 text-blue-700',
  completed:  'bg-green-100 text-green-700',
  failed:     'bg-red-100 text-red-700',
}

const JOB_STATUS_LABELS = {
  pending:    'Pendiente',
  processing: 'Procesando',
  completed:  'Completado',
  failed:     'Fallido',
}

const JOB_STATUS_DOTS = {
  pending:    'bg-gray-400',
  processing: 'bg-blue-500 animate-pulse',
  completed:  'bg-green-500',
  failed:     'bg-red-500',
}

const STATUSES = ['', 'pending', 'processing', 'completed', 'failed']

export default function JobsPage() {
  const { jobs, total, totalPages, loading, error, filters, updateFilter } = useJobs()

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Jobs de procesamiento</h1>
          <p className="text-gray-500 text-sm mt-1">{total} jobs en total</p>
        </div>
      </div>

      {/* Filtro por estado */}
      <div className="flex items-center gap-2 mb-6 flex-wrap">
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => updateFilter('status', s)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors border ${
              filters.status === s
                ? 'bg-brand-700 text-white border-brand-700'
                : 'bg-white text-gray-600 border-gray-200 hover:border-brand-500 hover:text-brand-700'
            }`}
          >
            {s === '' ? 'Todos' : JOB_STATUS_LABELS[s]}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner text="Cargando jobs..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-sm">{error}</div>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <p className="text-gray-400 text-sm">No hay jobs con este estado</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
            {/* Table header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-400 uppercase tracking-wide">
              <div className="col-span-4">Job ID</div>
              <div className="col-span-2">Estado</div>
              <div className="col-span-2 text-right">Documentos</div>
              <div className="col-span-2 text-right">Exitosos</div>
              <div className="col-span-2 text-right">Iniciado</div>
            </div>

            <div className="divide-y divide-gray-50">
              {jobs.map((job) => {
                const total_docs = job.result?.total ?? '—'
                const processed  = job.result?.processed ?? '—'

                return (
                  <Link
                    key={job.job_id}
                    to={`/jobs/${job.job_id}`}
                    className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-gray-50 transition-colors items-center"
                  >
                    {/* Job ID */}
                    <div className="col-span-4">
                      <p className="font-mono text-xs text-brand-700 truncate">{job.job_id}</p>
                      {job.completed_at && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Completado {formatDate(job.completed_at)}
                        </p>
                      )}
                    </div>

                    {/* Estado */}
                    <div className="col-span-2">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${JOB_STATUS_STYLES[job.status]}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${JOB_STATUS_DOTS[job.status]}`} />
                        {JOB_STATUS_LABELS[job.status] || job.status}
                      </span>
                    </div>

                    {/* Total docs */}
                    <div className="col-span-2 text-right">
                      <span className="text-sm font-semibold text-gray-700">{total_docs}</span>
                    </div>

                    {/* Procesados */}
                    <div className="col-span-2 text-right">
                      <span className={`text-sm font-semibold ${
                        typeof processed === 'number' && processed > 0 ? 'text-green-600' : 'text-gray-400'
                      }`}>
                        {processed}
                      </span>
                    </div>

                    {/* Fecha inicio */}
                    <div className="col-span-2 text-right">
                      <span className="text-xs text-gray-500">{formatDate(job.created_at)}</span>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>

          <Pagination
            page={filters.page}
            totalPages={totalPages}
            onPageChange={(p) => updateFilter('page', p)}
          />
        </>
      )}
    </div>
  )
}
