import { STATUS_LABELS, STATUS_COLORS } from '../../utils/formatters'

export default function StatusBadge({ status, size = 'sm' }) {
  const sizeClass = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'
  return (
    <span className={`inline-flex items-center font-medium rounded-full ${sizeClass} ${STATUS_COLORS[status] || 'bg-gray-100 text-gray-600'}`}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}
