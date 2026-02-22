import { Link } from 'react-router-dom'
import StatusBadge from '../common/StatusBadge'
import { formatCOP, formatDate, TYPE_LABELS } from '../../utils/formatters'

const SELECTABLE_STATUSES = ['draft', 'rejected']

export default function DocumentTable({ documents, selected, onToggle, onToggleAll }) {
  const selectableDocs = documents.filter((d) => SELECTABLE_STATUSES.includes(d.status))
  const allSelectableSelected =
    selectableDocs.length > 0 && selectableDocs.every((d) => selected.includes(d.id))

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 py-16 text-center">
        <svg className="w-10 h-10 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-gray-400 text-sm">No se encontraron documentos</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left">
              <input
                type="checkbox"
                checked={allSelectableSelected}
                onChange={() => onToggleAll(selectableDocs.map((d) => d.id))}
                className="rounded border-gray-300 text-brand-700 focus:ring-brand-700"
                title="Seleccionar borradores y rechazados"
              />
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">ID</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Tipo</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Monto</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Creado por</th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Fecha</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {documents.map((doc) => (
            <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3">
                {SELECTABLE_STATUSES.includes(doc.status) ? (
                  <input
                    type="checkbox"
                    checked={selected.includes(doc.id)}
                    onChange={() => onToggle(doc.id)}
                    className="rounded border-gray-300 text-brand-700 focus:ring-brand-700"
                  />
                ) : (
                  <span className="w-4 h-4 block" />
                )}
              </td>
              <td className="px-4 py-3 font-mono text-gray-500">#{doc.id}</td>
              <td className="px-4 py-3 text-gray-700">{TYPE_LABELS[doc.type] || doc.type}</td>
              <td className="px-4 py-3 font-semibold text-gray-800">{formatCOP(doc.amount)}</td>
              <td className="px-4 py-3"><StatusBadge status={doc.status} /></td>
              <td className="px-4 py-3 text-gray-500 max-w-[150px] truncate">{doc.created_by}</td>
              <td className="px-4 py-3 text-gray-400 text-xs">{formatDate(doc.created_at)}</td>
              <td className="px-4 py-3">
                <Link
                  to={`/documents/${doc.id}`}
                  className="text-brand-700 hover:underline text-xs font-medium"
                >
                  Ver →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
