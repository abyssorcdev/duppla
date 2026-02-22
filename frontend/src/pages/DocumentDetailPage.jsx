import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { documentsApi } from '../api/documents'
import StatusBadge from '../components/common/StatusBadge'
import LoadingSpinner from '../components/common/LoadingSpinner'
import DocumentForm from '../components/documents/DocumentForm'
import StatusChangeModal from '../components/documents/StatusChangeModal'
import { formatCOP, formatDate, TYPE_LABELS, VALID_TRANSITIONS } from '../utils/formatters'

export default function DocumentDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(false)
  const [editLoading, setEditLoading] = useState(false)
  const [editError, setEditError] = useState('')
  const [showStatusModal, setShowStatusModal] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await documentsApi.get(id)
      setDoc(data)
    } catch {
      setError('No se pudo cargar el documento')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [id])

  const handleUpdate = async (payload) => {
    setEditLoading(true)
    setEditError('')
    try {
      const { data } = await documentsApi.update(id, { ...payload, user_id: payload.created_by })
      setDoc(data)
      setEditing(false)
    } catch (err) {
      setEditError(err.response?.data?.detail || 'Error al actualizar')
    } finally {
      setEditLoading(false)
    }
  }

  const handleStatusChange = async (newStatus, comment) => {
    await documentsApi.changeStatus(id, newStatus, comment)
    await load()
  }

  if (loading) return <LoadingSpinner size="lg" text="Cargando documento..." />
  if (error) return (
    <div className="p-8">
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">{error}</div>
    </div>
  )

  const isDraft = doc.status === 'draft'
  const hasTransitions = (VALID_TRANSITIONS[doc.status] || []).length > 0

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {/* Back */}
      <Link to="/documents" className="text-sm text-brand-700 hover:underline">
        ← Volver a documentos
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between mt-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-800">Documento #{doc.id}</h1>
            <StatusBadge status={doc.status} size="lg" />
          </div>
          <p className="text-gray-500 text-sm mt-1">{TYPE_LABELS[doc.type] || doc.type}</p>
        </div>
        <div className="flex gap-2">
          {isDraft && !editing && (
            <button
              onClick={() => setEditing(true)}
              className="flex items-center gap-2 border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Editar
            </button>
          )}
          {hasTransitions && !editing && (
            <button
              onClick={() => setShowStatusModal(true)}
              className="flex items-center gap-2 bg-brand-700 hover:bg-brand-800 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              Cambiar estado
            </button>
          )}
        </div>
      </div>

      {editing ? (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">Editar documento</h2>
          {editError && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              {editError}
            </div>
          )}
          <DocumentForm
            initial={doc}
            onSubmit={handleUpdate}
            loading={editLoading}
            submitLabel="Guardar cambios"
          />
          <button
            onClick={() => setEditing(false)}
            className="mt-3 w-full text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Cancelar
          </button>
        </div>
      ) : (
        <>
          {/* Main info */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
            <div className="grid grid-cols-2 gap-6">
              <Field label="Monto" value={formatCOP(doc.amount)} highlight />
              <Field label="Tipo" value={TYPE_LABELS[doc.type] || doc.type} />
              <Field label="Creado por" value={doc.created_by} />
              <Field label="Creado el" value={formatDate(doc.created_at)} />
              {doc.updated_at && (
                <Field label="Actualizado el" value={formatDate(doc.updated_at)} />
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Metadata</h2>

            {doc.metadata && Object.keys(doc.metadata).length > 0 ? (
              <div className="space-y-3">
                {/* Highlighted metadata */}
                {doc.metadata.client && (
                  <MetaRow label="Cliente" value={doc.metadata.client} />
                )}
                {doc.metadata.email && (
                  <MetaRow label="Email" value={doc.metadata.email} />
                )}
                {doc.metadata.reference && (
                  <MetaRow label="Referencia" value={doc.metadata.reference} />
                )}

                {/* Rejection comment (manual review) */}
                {doc.metadata.rejection_comment && (
                  <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                      Rechazo manual
                    </p>
                    <MetaRow
                      label="Comentario"
                      value={<span className="text-red-600 dark:text-red-400">{doc.metadata.rejection_comment}</span>}
                    />
                    {doc.metadata.rejected_by && (
                      <MetaRow label="Rechazado por" value={doc.metadata.rejected_by} />
                    )}
                  </div>
                )}

                {/* Automated processing metadata */}
                {doc.metadata.processed_by_job && (
                  <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                      Procesamiento automático
                    </p>
                    <MetaRow
                      label="Job ID"
                      value={
                        <Link to={`/jobs/${doc.metadata.processed_by_job}`} className="text-brand-700 hover:underline font-mono text-xs">
                          {doc.metadata.processed_by_job}
                        </Link>
                      }
                    />
                    {doc.metadata.rejection_reason && (
                      <MetaRow
                        label="Motivo de rechazo"
                        value={<span className="text-red-600 dark:text-red-400">{doc.metadata.rejection_reason}</span>}
                      />
                    )}
                  </div>
                )}

                {/* Raw JSON */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">JSON completo</p>
                  <pre className="bg-gray-50 rounded-lg p-4 text-xs text-gray-600 overflow-auto">
                    {JSON.stringify(doc.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-400">Sin metadata</p>
            )}
          </div>
        </>
      )}

      {showStatusModal && (
        <StatusChangeModal
          document={doc}
          onClose={() => setShowStatusModal(false)}
          onSuccess={handleStatusChange}
        />
      )}
    </div>
  )
}

function Field({ label, value, highlight }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>
      <p className={`mt-1 ${highlight ? 'text-2xl font-bold text-gray-800' : 'text-sm text-gray-700'}`}>
        {value}
      </p>
    </div>
  )
}

function MetaRow({ label, value }) {
  return (
    <div className="flex items-start gap-3">
      <span className="text-xs font-medium text-gray-400 w-28 flex-shrink-0 pt-0.5">{label}</span>
      <span className="text-sm text-gray-700 break-all">{value}</span>
    </div>
  )
}
