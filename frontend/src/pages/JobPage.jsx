import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import useJobPolling from '../hooks/useJobPolling'
import { formatDate } from '../utils/formatters'

const JOB_STATUS_COLORS = {
  pending:    'bg-brand-100 text-brand-700',
  processing: 'bg-amber-100 text-amber-700',
  completed:  'bg-green-100 text-green-700',
  failed:     'bg-red-100 text-red-700',
}
const JOB_STATUS_LABELS = {
  pending:    'Pendiente',
  processing: 'Procesando',
  completed:  'Completado',
  failed:     'Fallido',
}

const IS_ACTIVE = ['pending', 'processing']

// ─── Animated dots ──────────────────────────────────────────────────────────
function AnimatedDots() {
  const [frame, setFrame] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setFrame((f) => (f + 1) % 4), 500)
    return () => clearInterval(t)
  }, [])
  return <span className="inline-block w-6 text-left">{'.'.repeat(frame)}</span>
}

// ─── Elapsed counter ─────────────────────────────────────────────────────────
function useElapsed(active) {
  const [secs, setSecs] = useState(0)
  useEffect(() => {
    if (!active) return
    const t = setInterval(() => setSecs((s) => s + 1), 1000)
    return () => clearInterval(t)
  }, [active])
  const m = Math.floor(secs / 60).toString().padStart(2, '0')
  const s = (secs % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// ─── Processing animation ─────────────────────────────────────────────────────
function ProcessingView({ job }) {
  const elapsed = useElapsed(IS_ACTIVE.includes(job.status))
  const docCount = job.result?.total ?? '—'

  return (
    <div className="flex flex-col items-center text-center w-full max-w-lg">
      {/* Concentric rings */}
      <div className="relative w-24 h-24 mb-5">
        <div className="absolute inset-0 rounded-full border-[3px] border-brand-100" />
        <div
          className="absolute inset-0 rounded-full border-[3px] border-transparent border-t-brand-500"
          style={{ animation: 'spin 2s linear infinite' }}
        />
        <div
          className="absolute inset-3 rounded-full border-[3px] border-transparent border-t-brand-700"
          style={{ animation: 'spin 1.4s linear infinite reverse' }}
        />
        <div className="absolute inset-0 rounded-full bg-brand-500/10 animate-ping" />
        <div className="absolute inset-0 flex items-center justify-center">
          <svg className="w-8 h-8 text-brand-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
      </div>

      {/* Título y subtítulo */}
      <h2 className="text-xl font-bold text-brand-900 flex items-baseline gap-0.5">
        Procesando documentos<AnimatedDots />
      </h2>
      <p className="text-brand-600 text-sm mt-1">
        {docCount !== '—' ? `${docCount} documentos en cola` : 'Calculando documentos...'}
      </p>

      {/* Timer */}
      <div className="mt-3 inline-flex items-center gap-1.5 bg-white border border-brand-100 rounded-full px-4 py-1.5 shadow-sm">
        <svg className="w-3.5 h-3.5 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="font-mono text-sm font-semibold text-brand-700">{elapsed}</span>
        <span className="text-xs text-brand-400">transcurrido</span>
      </div>

      {/* Skeleton rows */}
      <div className="mt-6 w-full max-w-lg space-y-2.5 text-left">
        {[0.9, 0.7, 1].map((delay, i) => (
          <div
            key={i}
            className="bg-white border border-brand-100 rounded-xl px-4 py-3 flex items-center gap-3 animate-pulse"
            style={{ animationDelay: `${delay * 0.4}s` }}
          >
            <div className="w-7 h-7 rounded-lg bg-brand-100 flex-shrink-0" />
            <div className="flex-1 space-y-1.5">
              <div className="h-2 bg-brand-100 rounded w-32" />
              <div className="h-1.5 bg-brand-50 rounded w-20" />
            </div>
            <div className="w-16 h-5 bg-brand-100 rounded-full" />
          </div>
        ))}
      </div>

      <p className="mt-4 text-xs text-brand-400 max-w-sm">
        Esta página se actualizará automáticamente al terminar.
      </p>
    </div>
  )
}

// ─── Results view ─────────────────────────────────────────────────────────────
function ResultsView({ job }) {
  const result   = job.result
  const total    = result?.total     ?? 0
  const processed = result?.processed ?? 0
  const failed   = result?.failed    ?? 0
  const pct      = total > 0 ? Math.round((processed / total) * 100) : 0
  const isOk     = job.status === 'completed'

  return (
    <>
      {/* Timeline */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <div className="grid grid-cols-2 gap-6 text-sm">
          <div>
            <p className="text-xs text-brand-600 uppercase tracking-wide font-semibold mb-1">Iniciado</p>
            <p className="text-brand-900">{formatDate(job.created_at)}</p>
          </div>
          <div>
            <p className="text-xs text-brand-600 uppercase tracking-wide font-semibold mb-1">Completado</p>
            <p className="text-brand-900">{job.completed_at ? formatDate(job.completed_at) : '—'}</p>
          </div>
        </div>
        {job.error_message && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            <span className="font-semibold">Error:</span> {job.error_message}
          </div>
        )}
      </div>

      {/* Progress */}
      {result && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-brand-600">{processed} de {total} documentos procesados</span>
            <span className="font-bold text-brand-900">{pct}%</span>
          </div>
          <div className="w-full bg-brand-50 rounded-full h-3 mb-5">
            <div
              className={`h-3 rounded-full transition-all duration-700 ${isOk ? 'bg-brand-700' : 'bg-red-500'}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <StatCard label="Total" value={total} color="text-brand-900" bg="bg-brand-50" />
            <StatCard label="Exitosos" value={processed} color="text-green-700" bg="bg-green-50" />
            <StatCard label="Fallidos" value={failed} color="text-red-600" bg="bg-red-50" />
          </div>
        </div>
      )}

      {/* Document results */}
      {result?.details && result.details.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-brand-900">Resultado por documento</h2>
          </div>
          <div className="divide-y divide-gray-50">
            {result.details.map((d) => (
              <div key={d.document_id} className="flex items-center justify-between px-6 py-3.5">
                <Link
                  to={`/documents/${d.document_id}`}
                  className="text-sm font-medium text-brand-700 hover:underline font-mono"
                >
                  #{d.document_id}
                </Link>
                <div className="flex items-center gap-3">
                  {d.error && (
                    <span className="text-xs text-red-500 bg-red-50 px-2 py-0.5 rounded font-mono">
                      {d.error}
                    </span>
                  )}
                  <span className={`inline-flex items-center gap-1 text-sm font-semibold ${
                    d.status === 'success' ? 'text-green-700' : 'text-red-600'
                  }`}>
                    {d.status === 'success' ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    {d.status === 'success' ? 'Exitoso' : 'Fallido'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function JobPage() {
  const { jobId } = useParams()
  const { job, loading, error } = useJobPolling(jobId)

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-full gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-brand-100 border-t-brand-700 animate-spin" />
        <p className="text-sm text-brand-600">Consultando job...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">{error}</div>
      </div>
    )
  }

  if (!job) return null

  const isActive = IS_ACTIVE.includes(job.status)

  return (
    <div className="flex flex-col min-h-full">
      {/* ── Header fijo arriba ── */}
      <div className="px-8 pt-6 pb-4 max-w-3xl w-full mx-auto">
        <Link to="/documents" className="text-sm text-brand-700 hover:underline flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Volver a documentos
        </Link>
        <div className="flex items-start justify-between mt-4">
          <div>
            <h1 className="text-xl font-bold text-brand-900">Job de procesamiento</h1>
            <p className="font-mono text-xs text-brand-400 mt-0.5 break-all">{job.job_id}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold flex-shrink-0 ml-4 ${JOB_STATUS_COLORS[job.status]}`}>
            {JOB_STATUS_LABELS[job.status] || job.status}
          </span>
        </div>
      </div>

      {/* ── Contenido: centrado verticalmente si está activo ── */}
      {isActive ? (
        <div className="flex-1 flex items-center justify-center px-8 pb-8">
          <ProcessingView job={job} />
        </div>
      ) : (
        <div className="px-8 pb-8 max-w-3xl w-full mx-auto">
          <ResultsView job={job} />
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, color, bg }) {
  return (
    <div className={`${bg} rounded-xl py-4`}>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-brand-600 mt-0.5">{label}</p>
    </div>
  )
}
