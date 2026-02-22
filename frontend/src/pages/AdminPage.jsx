import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { adminApi } from '../api/admin'
import { formatDate } from '../utils/formatters'

// ── Constants ──────────────────────────────────────────────────────────────────
const STATUS_LABELS = { pending: 'Pendiente', active: 'Activo', disabled: 'Deshabilitado' }
const STATUS_COLORS = {
  pending:  'bg-amber-50 text-amber-700 border-amber-200',
  active:   'bg-green-50 text-green-700 border-green-200',
  disabled: 'bg-gray-100 text-gray-500 border-gray-200',
}
const ROLE_LABELS = { admin: 'Administrador', loader: 'Cargador', approver: 'Aprobador' }
const ACTION_LABELS = {
  created:       'Creación',
  state_change:  'Cambio de estado',
  field_updated: 'Campo editado',
  updated:       'Actualización',
  deleted:       'Eliminación',
}
const ACTION_COLORS = {
  created:       'bg-green-50 text-green-700',
  state_change:  'bg-blue-100 text-blue-700',
  field_updated: 'bg-amber-50 text-amber-700',
  updated:       'bg-brand-100 text-brand-700',
  deleted:       'bg-red-50 text-red-700',
}

// ── User management ────────────────────────────────────────────────────────────
function RoleSelect({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="text-sm border border-gray-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-brand-700"
    >
      <option value="">— Seleccionar rol —</option>
      <option value="admin">Administrador</option>
      <option value="loader">Cargador</option>
      <option value="approver">Aprobador</option>
    </select>
  )
}

function UserRow({ user, onApprove, onDisable, approving }) {
  const [selectedRole, setSelectedRole] = useState(user.role || '')

  return (
    <tr className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
      <td className="px-5 py-3.5">
        <div className="flex items-center gap-3">
          {user.picture ? (
            <img src={user.picture} alt="" className="w-8 h-8 rounded-full flex-shrink-0" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
              <span className="text-brand-700 text-xs font-semibold">
                {user.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
          )}
          <div>
            <p className="text-sm font-medium text-gray-800">{user.name}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>
        </div>
      </td>
      <td className="px-5 py-3.5">
        <span className={`inline-flex items-center text-xs font-medium px-2.5 py-1 rounded-full border ${STATUS_COLORS[user.status]}`}>
          {STATUS_LABELS[user.status] || user.status}
        </span>
      </td>
      <td className="px-5 py-3.5 text-sm text-gray-600">
        {user.role ? ROLE_LABELS[user.role] : <span className="text-gray-400 italic">Sin asignar</span>}
      </td>
      <td className="px-5 py-3.5">
        <div className="flex items-center gap-2 flex-wrap">
          {user.status !== 'disabled' && (
            <>
              <RoleSelect value={selectedRole} onChange={setSelectedRole} />
              <button
                disabled={!selectedRole || approving === user.id}
                onClick={() => onApprove(user.id, selectedRole)}
                className="text-xs font-semibold bg-brand-700 hover:bg-brand-800 disabled:opacity-40 text-white px-3 py-1.5 rounded-lg transition-colors"
              >
                {approving === user.id ? 'Guardando...' : user.status === 'pending' ? 'Aprobar' : 'Cambiar rol'}
              </button>
            </>
          )}
          {user.status === 'active' && (
            <button
              disabled={approving === user.id}
              onClick={() => onDisable(user.id)}
              className="text-xs font-semibold text-red-600 hover:text-red-700 border border-red-200 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-40"
            >
              Deshabilitar
            </button>
          )}
          {user.status === 'disabled' && (
            <>
              <RoleSelect value={selectedRole} onChange={setSelectedRole} />
              <button
                disabled={!selectedRole || approving === user.id}
                onClick={() => onApprove(user.id, selectedRole)}
                className="text-xs font-semibold bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white px-3 py-1.5 rounded-lg transition-colors"
              >
                Rehabilitar
              </button>
            </>
          )}
        </div>
      </td>
    </tr>
  )
}

function UsersTab() {
  const [users, setUsers]       = useState([])
  const [total, setTotal]       = useState(0)
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [approving, setApproving] = useState(null)
  const [filter, setFilter]     = useState('')

  const fetch = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const { data } = await adminApi.listUsers(filter ? { status: filter } : {})
      setUsers(data.items); setTotal(data.total)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar usuarios')
    } finally { setLoading(false) }
  }, [filter])

  useEffect(() => { fetch() }, [fetch])

  const handleApprove = async (userId, role) => {
    setApproving(userId)
    try { await adminApi.approveUser(userId, role); await fetch() }
    catch (err) { setError(err.response?.data?.detail || 'Error al aprobar usuario') }
    finally { setApproving(null) }
  }

  const handleDisable = async (userId) => {
    setApproving(userId)
    try { await adminApi.disableUser(userId); await fetch() }
    catch (err) { setError(err.response?.data?.detail || 'Error al deshabilitar usuario') }
    finally { setApproving(null) }
  }

  const pendingCount = users.filter((u) => u.status === 'pending').length

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total',      value: total,                                          color: 'text-brand-900' },
          { label: 'Pendientes', value: pendingCount,                                   color: 'text-amber-600' },
          { label: 'Activos',    value: users.filter(u => u.status === 'active').length, color: 'text-green-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-sm text-gray-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-3">
          <h2 className="font-semibold text-gray-800 flex-1">Usuarios</h2>
          {['', 'pending', 'active', 'disabled'].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                filter === s ? 'bg-brand-700 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {s === '' ? 'Todos' : STATUS_LABELS[s]}
            </button>
          ))}
        </div>
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 rounded-full border-4 border-brand-100 border-t-brand-700 animate-spin" />
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-16 text-gray-400 text-sm">
            No hay usuarios {filter ? `con estado "${STATUS_LABELS[filter]}"` : ''}.
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide border-b border-gray-100">
                <th className="px-5 py-3">Usuario</th>
                <th className="px-5 py-3">Estado</th>
                <th className="px-5 py-3">Rol actual</th>
                <th className="px-5 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <UserRow key={u.id} user={u} onApprove={handleApprove} onDisable={handleDisable} approving={approving} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

// ── Audit logs tab ─────────────────────────────────────────────────────────────
function LogsTab() {
  const [logs, setLogs]             = useState([])
  const [total, setTotal]           = useState(0)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState('')
  const [filter, setFilter]         = useState('')       // table_name filter
  const [actionFilter, setActionFilter] = useState('')  // action filter
  const [page, setPage]             = useState(0)
  const LIMIT = 50

  const fetch = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params = {
        skip: page * LIMIT,
        limit: LIMIT,
        ...(filter ? { table_name: filter } : {}),
        ...(actionFilter ? { action: actionFilter } : {}),
      }
      const { data } = await adminApi.listLogs(params)
      setLogs(data.items); setTotal(data.total)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al cargar logs')
    } finally { setLoading(false) }
  }, [filter, actionFilter, page])

  useEffect(() => { fetch() }, [fetch])

  const TABLE_LABELS = { documents: 'Documentos', jobs: 'Jobs', users: 'Usuarios' }
const TABLE_FILTERS = ['', 'documents', 'jobs', 'users']
const ACTION_FILTERS = ['', 'created', 'state_change', 'field_updated']

  return (
    <div className="space-y-5">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2 flex-wrap">
          <h2 className="font-semibold text-gray-800 flex-1">
            Registros de auditoría
            <span className="ml-2 text-xs text-gray-400 font-normal">{total} entradas</span>
          </h2>
          <div className="flex items-center gap-1.5 flex-wrap">
            {TABLE_FILTERS.map((t) => (
              <button
                key={t}
                onClick={() => { setFilter(t); setPage(0) }}
                className={`text-xs px-2.5 py-1.5 rounded-full font-medium transition-colors ${
                  filter === t ? 'bg-brand-700 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {t === '' ? 'Todas las tablas' : TABLE_LABELS[t] || t}
              </button>
            ))}
          </div>
          <div className="w-px h-5 bg-gray-200" />
          <div className="flex items-center gap-1.5 flex-wrap">
            {ACTION_FILTERS.map((a) => (
              <button
                key={a}
                onClick={() => { setActionFilter(a); setPage(0) }}
                className={`text-xs px-2.5 py-1.5 rounded-full font-medium transition-colors ${
                  actionFilter === a ? 'bg-brand-700 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {a === '' ? 'Todas las acciones' : ACTION_LABELS[a] || a}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 rounded-full border-4 border-brand-100 border-t-brand-700 animate-spin" />
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-16 text-gray-400 text-sm">No hay registros.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide border-b border-gray-100">
                <th className="px-5 py-3">Fecha</th>
                <th className="px-5 py-3">Tabla</th>
                <th className="px-5 py-3">Acción</th>
                <th className="px-5 py-3">Registro</th>
                <th className="px-5 py-3">Detalle</th>
                <th className="px-5 py-3">Usuario</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors text-sm">
                  <td className="px-5 py-3 text-gray-500 whitespace-nowrap text-xs">
                    {formatDate(log.timestamp)}
                  </td>
                  <td className="px-5 py-3">
                    <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                      {TABLE_LABELS[log.table_name] || log.table_name}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span className={`inline-flex text-xs font-medium px-2.5 py-1 rounded-full ${ACTION_COLORS[log.action] || 'bg-gray-100 text-gray-600'}`}>
                      {ACTION_LABELS[log.action] || log.action}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    {log.table_name === 'documents' ? (
                      <Link to={`/documents/${log.record_id}`} className="text-brand-700 hover:underline font-mono text-xs">
                        #{log.record_id}
                      </Link>
                    ) : (
                      <span className="font-mono text-xs text-gray-500">{log.record_id.slice(0, 8)}…</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-gray-600 text-xs max-w-xs">
                    {log.old_value && log.new_value ? (
                      <span>
                        <span className="line-through text-gray-400">{log.old_value}</span>
                        {' → '}
                        <span className="text-gray-700">{log.new_value}</span>
                      </span>
                    ) : (
                      <span>{log.new_value || log.old_value || '—'}</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-gray-500 text-xs truncate max-w-[140px]">
                    {log.user_id || <span className="italic text-gray-300">sistema</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {total > LIMIT && (
          <div className="px-5 py-3 border-t border-gray-100 flex items-center justify-between text-sm text-gray-500">
            <span>{page * LIMIT + 1}–{Math.min((page + 1) * LIMIT, total)} de {total}</span>
            <div className="flex gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 text-xs"
              >
                Anterior
              </button>
              <button
                disabled={(page + 1) * LIMIT >= total}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 text-xs"
              >
                Siguiente
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────────
const TABS = [
  { id: 'users', label: 'Usuarios' },
  { id: 'logs',  label: 'Logs del sistema' },
]

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('users')

  return (
    <div className="px-8 pt-6 pb-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Panel de administración</h1>
        <p className="text-gray-500 text-sm mt-1">
          Gestiona usuarios, roles y revisa la actividad del sistema.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 w-fit">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === id
                ? 'bg-white text-brand-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'users' ? <UsersTab /> : <LogsTab />}
    </div>
  )
}
