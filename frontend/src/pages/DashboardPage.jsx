import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { documentsApi } from '../api/documents'
import { jobsApi } from '../api/jobs'
import { formatCOP, formatDate, STATUS_LABELS, STATUS_COLORS } from '../utils/formatters'
import LoadingSpinner from '../components/common/LoadingSpinner'

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

const STATUSES = ['draft', 'pending', 'approved', 'rejected']

const STATUS_ICONS = {
  draft: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  ),
  pending: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  ),
  approved: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  ),
  rejected: (
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
      d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
  ),
}

export default function DashboardPage() {
  const [stats, setStats] = useState({})
  const [recent, setRecent] = useState([])
  const [recentJobs, setRecentJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [jobsRes, ...statusResults] = await Promise.all([
          jobsApi.list({ page_size: 5, page: 1 }),
          ...STATUSES.map((s) => documentsApi.list({ status: s, page_size: 1 })),
        ])
        setRecentJobs(jobsRes.data.items)

        const counts = {}
        STATUSES.forEach((s, i) => { counts[s] = statusResults[i].data.total })
        setStats(counts)

        const { data } = await documentsApi.list({ page_size: 5, page: 1 })
        setRecent(data.items)
      } catch {
        // silently handle
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <LoadingSpinner size="lg" text="Cargando dashboard..." />

  const total = Object.values(stats).reduce((a, b) => a + b, 0)

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-brand-900">Dashboard</h1>
        <p className="text-brand-600 text-sm mt-1">Resumen de documentos en el sistema</p>
      </div>

      {/* Total card */}
      <div className="relative overflow-hidden bg-brand-700 rounded-2xl p-6 text-white mb-6">
        {/* decorative circles */}
        <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full bg-brand-500/20" />
        <div className="absolute -bottom-10 -right-2 w-28 h-28 rounded-full bg-brand-800/40" />
        <div className="relative">
          <p className="text-brand-300 text-sm font-medium uppercase tracking-wider">Total de documentos</p>
          <p className="text-6xl font-bold mt-1 leading-none">{total}</p>
          <Link
            to="/documents"
            className="mt-5 inline-flex items-center gap-1.5 text-sm font-medium text-brand-300 hover:text-white transition-colors"
          >
            Ver todos los documentos
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {STATUSES.map((status) => (
          <Link
            key={status}
            to={`/documents?status=${status}`}
            className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {STATUS_LABELS[status]}
                </p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats[status] ?? 0}</p>
              </div>
              <span className={`inline-flex p-2 rounded-lg ${STATUS_COLORS[status]}`}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {STATUS_ICONS[status]}
                </svg>
              </span>
            </div>
            {total > 0 && (
              <div className="mt-3">
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-brand-500"
                    style={{ width: `${((stats[status] ?? 0) / total) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {total > 0 ? Math.round(((stats[status] ?? 0) / total) * 100) : 0}% del total
                </p>
              </div>
            )}
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent documents */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">Documentos recientes</h2>
            <Link to="/documents" className="text-sm text-brand-700 hover:underline">Ver todos</Link>
          </div>
          {recent.length === 0 ? (
            <div className="px-6 py-10 text-center text-gray-400 text-sm">
              No hay documentos aún.{' '}
              <Link to="/documents/new" className="text-brand-700 hover:underline">Crea el primero</Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-50">
              {recent.map((doc) => (
                <Link
                  key={doc.id}
                  to={`/documents/${doc.id}`}
                  className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-800">#{doc.id} — {doc.type}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{doc.created_by}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-semibold text-gray-700">{formatCOP(doc.amount)}</span>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_COLORS[doc.status]}`}>
                      {STATUS_LABELS[doc.status]}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent jobs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">Jobs recientes</h2>
            <Link to="/jobs" className="text-sm text-brand-700 hover:underline">Ver todos</Link>
          </div>
          {recentJobs.length === 0 ? (
            <div className="px-6 py-10 text-center text-gray-400 text-sm">
              No hay jobs ejecutados aún.
            </div>
          ) : (
            <div className="divide-y divide-gray-50">
              {recentJobs.map((job) => (
                <Link
                  key={job.job_id}
                  to={`/jobs/${job.job_id}`}
                  className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-xs text-brand-700 truncate">{job.job_id}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{formatDate(job.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-3 ml-4 flex-shrink-0">
                    {job.result && (
                      <span className="text-xs text-gray-500">
                        {job.result.processed ?? 0}/{job.result.total ?? 0} docs
                      </span>
                    )}
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${JOB_STATUS_STYLES[job.status]}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${JOB_STATUS_DOTS[job.status]}`} />
                      {JOB_STATUS_LABELS[job.status] || job.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
