import { useState } from 'react'
import { TYPE_LABELS } from '../../utils/formatters'

const TYPES = Object.keys(TYPE_LABELS)

const extraMetaPlaceholder = `{
  "region": "Bogotá",
  "departamento": "Cundinamarca"
}`

function buildExtraInitial(metadata) {
  if (!metadata) return ''
  const reserved = ['client', 'email', 'reference', 'processed_by_job', 'rejection_reason']
  const extra = Object.fromEntries(
    Object.entries(metadata).filter(([k]) => !reserved.includes(k))
  )
  return Object.keys(extra).length ? JSON.stringify(extra, null, 2) : ''
}

function Field({ label, required, hint, error, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        {label}
        {required && <span className="text-brand-700 ml-0.5">*</span>}
        {hint && <span className="ml-1.5 text-gray-400 font-normal text-xs">{hint}</span>}
      </label>
      {children}
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  )
}

const inputBase =
  'w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm bg-white ' +
  'focus:outline-none focus:ring-2 focus:ring-brand-700 focus:border-transparent ' +
  'transition-colors placeholder:text-gray-400'

export default function DocumentForm({ initial = {}, onSubmit, loading, submitLabel = 'Guardar' }) {
  const [form, setForm] = useState({
    type: initial.type || 'invoice',
    amount: initial.amount || '',
    created_by: initial.created_by || '',
    metadata_client: initial.metadata?.client || '',
    metadata_email: initial.metadata?.email || '',
    metadata_reference: initial.metadata?.reference || '',
    metadata_extra: buildExtraInitial(initial.metadata),
  })
  const [errors, setErrors] = useState({})

  const set = (key, val) => {
    setForm((p) => ({ ...p, [key]: val }))
    setErrors((p) => ({ ...p, [key]: '' }))
  }

  const validate = () => {
    const e = {}
    if (!form.type) e.type = 'Requerido'
    if (!form.amount || Number(form.amount) <= 0) e.amount = 'Debe ser mayor a 0'
    if (!form.created_by.trim()) e.created_by = 'Requerido'
    if (!form.metadata_client.trim()) e.metadata_client = 'Requerido para procesamiento automático'
    if (!form.metadata_email.trim()) e.metadata_email = 'Requerido para procesamiento automático'
    if (form.metadata_extra.trim()) {
      try {
        const parsed = JSON.parse(form.metadata_extra)
        if (typeof parsed !== 'object' || Array.isArray(parsed)) {
          e.metadata_extra = 'Debe ser un objeto JSON, ej: { "clave": "valor" }'
        }
      } catch {
        e.metadata_extra = 'JSON inválido — verifica la sintaxis'
      }
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return

    let extra = {}
    if (form.metadata_extra.trim()) {
      try { extra = JSON.parse(form.metadata_extra) } catch { /* validated above */ }
    }

    onSubmit({
      type: form.type,
      amount: parseFloat(form.amount),
      created_by: form.created_by.trim(),
      metadata: {
        client: form.metadata_client.trim(),
        email: form.metadata_email.trim(),
        ...(form.metadata_reference ? { reference: form.metadata_reference.trim() } : {}),
        ...extra,
      },
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">

      {/* ── Información básica ─────────────────────────────────────── */}
      <div className="space-y-4">
        <Field label="Tipo de documento" required error={errors.type}>
          <select
            value={form.type}
            onChange={(e) => set('type', e.target.value)}
            className={inputBase}
          >
            {TYPES.map((t) => <option key={t} value={t}>{TYPE_LABELS[t]}</option>)}
          </select>
        </Field>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Monto (COP)" required error={errors.amount}>
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.amount}
              onChange={(e) => set('amount', e.target.value)}
              placeholder="150 000"
              className={inputBase}
            />
          </Field>

          <Field label="Creado por" required error={errors.created_by}>
            <input
              type="text"
              value={form.created_by}
              onChange={(e) => set('created_by', e.target.value)}
              placeholder="user@empresa.com"
              className={inputBase}
            />
          </Field>
        </div>
      </div>

      {/* ── Metadata ───────────────────────────────────────────────── */}
      <div className="border-t border-gray-100 pt-5 space-y-4">
        <div>
          <p className="text-xs font-semibold text-brand-700 uppercase tracking-widest">
            Metadata
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            Requerida para el procesamiento automático en batch.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Field label="Cliente" required error={errors.metadata_client}>
            <input
              type="text"
              value={form.metadata_client}
              onChange={(e) => set('metadata_client', e.target.value)}
              placeholder="Empresa ABC"
              className={inputBase}
            />
          </Field>

          <Field label="Email" required error={errors.metadata_email}>
            <input
              type="email"
              value={form.metadata_email}
              onChange={(e) => set('metadata_email', e.target.value)}
              placeholder="pagos@empresa.com"
              className={inputBase}
            />
          </Field>
        </div>

        <Field label="Referencia" hint="(opcional)">
          <input
            type="text"
            value={form.metadata_reference}
            onChange={(e) => set('metadata_reference', e.target.value)}
            placeholder="INV-2024-001"
            className={inputBase}
          />
        </Field>

        <Field
          label="Campos adicionales"
          hint="(JSON libre, opcional)"
          error={errors.metadata_extra}
        >
          <textarea
            rows={3}
            value={form.metadata_extra}
            onChange={(e) => set('metadata_extra', e.target.value)}
            placeholder={extraMetaPlaceholder}
            spellCheck={false}
            className={`${inputBase} font-mono resize-y ${
              errors.metadata_extra ? 'border-red-400' : ''
            }`}
          />
          {!errors.metadata_extra && (
            <p className="text-gray-400 text-xs mt-1">
              Se combina con los campos anteriores.{' '}
              <code className="bg-gray-100 px-1 rounded text-gray-500">client</code> y{' '}
              <code className="bg-gray-100 px-1 rounded text-gray-500">email</code> no se sobreescriben.
            </p>
          )}
        </Field>
      </div>

      {/* ── Acción ─────────────────────────────────────────────────── */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-brand-700 hover:bg-brand-800 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors"
      >
        {loading ? 'Guardando...' : submitLabel}
      </button>
    </form>
  )
}
