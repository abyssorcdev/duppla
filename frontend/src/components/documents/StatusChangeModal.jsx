import { useState } from 'react'
import { VALID_TRANSITIONS, STATUS_LABELS } from '../../utils/formatters'
import ConfirmModal from '../common/ConfirmModal'

export default function StatusChangeModal({ document, onClose, onSuccess }) {
  const [newStatus, setNewStatus] = useState('')
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const transitions = VALID_TRANSITIONS[document.status] || []
  const isRejecting = newStatus === 'rejected'

  const handleConfirm = async () => {
    if (!newStatus) { setError('Selecciona un estado'); return }
    if (isRejecting && !comment.trim()) { setError('El comentario de rechazo es obligatorio'); return }
    setLoading(true)
    setError('')
    try {
      await onSuccess(newStatus, isRejecting ? comment.trim() : null)
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cambiar estado')
    } finally {
      setLoading(false)
    }
  }

  return (
    <ConfirmModal
      title="Cambiar estado del documento"
      confirmLabel="Cambiar estado"
      confirmClass="bg-brand-700 hover:bg-brand-800"
      onConfirm={handleConfirm}
      onCancel={onClose}
      loading={loading}
    >
      <div className="space-y-4 my-2">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Estado actual: <span className="font-semibold text-gray-700 dark:text-gray-200">{STATUS_LABELS[document.status]}</span>
        </p>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nuevo estado</label>
          <select
            value={newStatus}
            onChange={(e) => { setNewStatus(e.target.value); setError('') }}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 bg-white dark:bg-gray-800 dark:text-gray-200"
          >
            <option value="">Seleccionar...</option>
            {transitions.map((s) => (
              <option key={s} value={s}>{STATUS_LABELS[s]}</option>
            ))}
          </select>
        </div>

        {isRejecting && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Motivo del rechazo <span className="text-red-400">*</span>
            </label>
            <textarea
              value={comment}
              onChange={(e) => { setComment(e.target.value); setError('') }}
              placeholder="Explica la razón del rechazo..."
              rows={3}
              maxLength={500}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 bg-white dark:bg-gray-800 dark:text-gray-200 resize-none"
            />
            <p className="text-xs text-gray-400 mt-1 text-right">{comment.length}/500</p>
          </div>
        )}

        {error && <p className="text-red-500 text-sm">{error}</p>}
      </div>
    </ConfirmModal>
  )
}
