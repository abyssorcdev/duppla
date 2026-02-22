import { TYPE_LABELS, STATUS_LABELS } from '../../utils/formatters'

const TYPES = Object.keys(TYPE_LABELS)
const STATUSES = ['draft', 'pending', 'approved', 'rejected']

export default function FilterBar({ filters, onFilterChange }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-wrap gap-3 items-end">
      {/* Type */}
      <div className="flex flex-col gap-1 min-w-[140px]">
        <label className="text-xs font-medium text-gray-500">Tipo</label>
        <select
          value={filters.type || ''}
          onChange={(e) => onFilterChange('type', e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 bg-white"
        >
          <option value="">Todos</option>
          {TYPES.map((t) => (
            <option key={t} value={t}>{TYPE_LABELS[t]}</option>
          ))}
        </select>
      </div>

      {/* Status */}
      <div className="flex flex-col gap-1 min-w-[140px]">
        <label className="text-xs font-medium text-gray-500">Estado</label>
        <select
          value={filters.status || ''}
          onChange={(e) => onFilterChange('status', e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 bg-white"
        >
          <option value="">Todos</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{STATUS_LABELS[s]}</option>
          ))}
        </select>
      </div>

      {/* Amount min */}
      <div className="flex flex-col gap-1 min-w-[130px]">
        <label className="text-xs font-medium text-gray-500">Monto mínimo</label>
        <input
          type="number"
          placeholder="0"
          value={filters.amount_min || ''}
          onChange={(e) => onFilterChange('amount_min', e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700"
        />
      </div>

      {/* Amount max */}
      <div className="flex flex-col gap-1 min-w-[130px]">
        <label className="text-xs font-medium text-gray-500">Monto máximo</label>
        <input
          type="number"
          placeholder="Sin límite"
          value={filters.amount_max || ''}
          onChange={(e) => onFilterChange('amount_max', e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700"
        />
      </div>

      {/* Clear */}
      <button
        onClick={() => {
          onFilterChange('type', '')
          onFilterChange('status', '')
          onFilterChange('amount_min', '')
          onFilterChange('amount_max', '')
        }}
        className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
      >
        Limpiar filtros
      </button>
    </div>
  )
}
