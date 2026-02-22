import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { documentsApi } from '../api/documents'
import DocumentForm from '../components/documents/DocumentForm'

export default function DocumentCreatePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (payload) => {
    setLoading(true)
    setError('')
    try {
      const { data } = await documentsApi.create(payload)
      navigate(`/documents/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear el documento')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-xl mx-auto">
      <Link to="/documents" className="inline-flex items-center gap-1.5 text-sm text-brand-700 hover:underline mb-6">
        ← Volver a documentos
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Nuevo Documento</h1>
        <p className="text-gray-500 text-sm mt-1">
          Completa los datos del documento para registrarlo en el sistema.
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-7">
        {error && (
          <div className="mb-5 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <DocumentForm
          onSubmit={handleSubmit}
          loading={loading}
          submitLabel="Crear documento"
        />
      </div>
    </div>
  )
}
