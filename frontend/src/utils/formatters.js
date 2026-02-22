export const STATUS_LABELS = {
  draft: 'Borrador',
  pending: 'En revisión',
  approved: 'Aprobado',
  rejected: 'Rechazado',
}

export const STATUS_COLORS = {
  draft:    'bg-brand-100 text-brand-700',
  pending:  'bg-amber-100 text-amber-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-700',
}

export const TYPE_LABELS = {
  invoice: 'Factura',
  receipt: 'Recibo',
  voucher: 'Comprobante',
  credit_note: 'Nota Crédito',
  debit_note: 'Nota Débito',
}

export const VALID_TRANSITIONS = {
  draft: ['pending'],
  pending: ['approved', 'rejected'],
  approved: [],
  rejected: [],
}

export function formatCOP(amount) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateStr))
}
