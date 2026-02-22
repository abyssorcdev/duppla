import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { documentsApi } from '../../api/documents'
import ConfirmModal from '../common/ConfirmModal'

export default function BatchModal({ documentIds, onClose, onSuccess }) {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleConfirm = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await documentsApi.processBatch(documentIds)
      onSuccess()
      onClose()
      navigate(`/jobs/${data.job_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar el procesamiento')
      setLoading(false)
    }
  }

  return (
    <ConfirmModal
      title="Procesar documentos en batch"
      confirmLabel="Iniciar procesamiento"
      confirmClass="bg-brand-700 hover:bg-brand-800"
      onConfirm={handleConfirm}
      onCancel={onClose}
      loading={loading}
    >
      <div className="my-3 space-y-3">
        <p className="text-sm text-gray-500">
          Se enviarán <span className="font-semibold text-gray-700">{documentIds.length} documentos</span> para
          procesamiento asíncrono.
        </p>

        <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-xs text-amber-800">
          <p className="font-semibold mb-1">Comportamiento por estado:</p>
          <ul className="list-disc list-inside space-y-0.5">
            <li><span className="font-semibold">Borrador</span> → evaluado → pasa a <em>En revisión</em> o <em>Rechazado</em></li>
            <li><span className="font-semibold">Rechazado</span> → vuelve a <em>Borrador</em> para corrección</li>
          </ul>
        </div>

        <div className="bg-gray-50 border border-gray-100 rounded-lg px-4 py-3 text-xs text-gray-600">
          <p className="font-semibold mb-1">Reglas de rechazo automático (borradores):</p>
          <ul className="list-disc list-inside space-y-0.5">
            <li>Monto mayor a $10,000,000 COP</li>
            <li>Metadata sin <code className="font-mono">client</code> o <code className="font-mono">email</code></li>
          </ul>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1.5">IDs seleccionados:</p>
          <div className="flex flex-wrap gap-1.5">
            {documentIds.map((id) => (
              <span key={id} className="bg-brand-100 text-brand-700 text-xs font-mono px-2 py-0.5 rounded">
                #{id}
              </span>
            ))}
          </div>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}
      </div>
    </ConfirmModal>
  )
}
