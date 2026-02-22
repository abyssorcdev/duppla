import { describe, it, expect } from 'vitest'
import {
  STATUS_LABELS,
  TYPE_LABELS,
  VALID_TRANSITIONS,
  formatCOP,
  formatDate,
} from './formatters'

describe('STATUS_LABELS', () => {
  it('should have labels for all statuses', () => {
    expect(STATUS_LABELS.draft).toBe('Borrador')
    expect(STATUS_LABELS.pending).toBe('En revisión')
    expect(STATUS_LABELS.approved).toBe('Aprobado')
    expect(STATUS_LABELS.rejected).toBe('Rechazado')
  })
})

describe('TYPE_LABELS', () => {
  it('should have labels for all document types', () => {
    expect(TYPE_LABELS.invoice).toBe('Factura')
    expect(TYPE_LABELS.receipt).toBe('Recibo')
    expect(TYPE_LABELS.voucher).toBe('Comprobante')
    expect(TYPE_LABELS.credit_note).toBe('Nota Crédito')
    expect(TYPE_LABELS.debit_note).toBe('Nota Débito')
  })
})

describe('VALID_TRANSITIONS', () => {
  it('draft can go to pending', () => {
    expect(VALID_TRANSITIONS.draft).toContain('pending')
  })

  it('pending can go to approved or rejected', () => {
    expect(VALID_TRANSITIONS.pending).toEqual(['approved', 'rejected'])
  })

  it('approved is final', () => {
    expect(VALID_TRANSITIONS.approved).toEqual([])
  })

  it('rejected is final', () => {
    expect(VALID_TRANSITIONS.rejected).toEqual([])
  })
})

describe('formatCOP', () => {
  it('should format a number as COP currency', () => {
    const result = formatCOP(1000000)
    expect(result).toContain('1.000.000')
  })

  it('should format zero', () => {
    const result = formatCOP(0)
    expect(result).toContain('0')
  })

  it('should format large amounts', () => {
    const result = formatCOP(50000000)
    expect(result).toContain('50.000.000')
  })
})

describe('formatDate', () => {
  it('should return dash for null/undefined', () => {
    expect(formatDate(null)).toBe('—')
    expect(formatDate(undefined)).toBe('—')
    expect(formatDate('')).toBe('—')
  })

  it('should format a valid date string', () => {
    const result = formatDate('2025-06-15T10:30:00')
    expect(result).toBeTruthy()
    expect(result).not.toBe('—')
  })
})
