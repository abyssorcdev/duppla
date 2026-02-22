import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import useDocuments from '../hooks/useDocuments'
import DocumentTable from '../components/documents/DocumentTable'
import FilterBar from '../components/documents/FilterBar'
import Pagination from '../components/common/Pagination'
import LoadingSpinner from '../components/common/LoadingSpinner'
import BatchModal from '../components/batch/BatchModal'

export default function DocumentsPage() {
  const [searchParams] = useSearchParams()
  const [selected, setSelected] = useState([])
  const [showBatch, setShowBatch] = useState(false)

  const { documents, total, totalPages, loading, error, filters, updateFilter, refresh } =
    useDocuments({ status: searchParams.get('status') || '' })

  useEffect(() => { setSelected([]) }, [filters])

  const toggleOne = (id) =>
    setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id])

  const toggleAll = (ids) => {
    const allSelected = ids.every((id) => selected.includes(id))
    setSelected(allSelected ? selected.filter((id) => !ids.includes(id)) : [...new Set([...selected, ...ids])])
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Documentos</h1>
          <p className="text-gray-500 text-sm mt-1">{total} documentos encontrados</p>
        </div>
        <div className="flex items-center gap-3">
          {selected.length > 0 && (
            <button
              onClick={() => setShowBatch(true)}
              className="flex items-center gap-2 bg-brand-700 hover:bg-brand-800 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Procesar batch ({selected.length})
            </button>
          )}
          <Link
            to="/documents/new"
            className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + Nuevo
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-4">
        <FilterBar filters={filters} onFilterChange={updateFilter} />
      </div>

      {/* Table */}
      {loading ? (
        <LoadingSpinner text="Cargando documentos..." />
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700 text-sm">{error}</div>
      ) : (
        <>
          <DocumentTable
            documents={documents}
            selected={selected}
            onToggle={toggleOne}
            onToggleAll={toggleAll}
          />
          <Pagination
            page={filters.page}
            totalPages={totalPages}
            onPageChange={(p) => updateFilter('page', p)}
          />
        </>
      )}

      {showBatch && (
        <BatchModal
          documentIds={selected}
          onClose={() => setShowBatch(false)}
          onSuccess={() => { setSelected([]); refresh() }}
        />
      )}
    </div>
  )
}
