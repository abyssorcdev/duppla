import { useAuthContext } from '../context/AuthContext'

const ROLE_LABELS = {
  admin:    'Administrador',
  loader:   'Cargador',
  approver: 'Aprobador',
}

/**
 * Convenience hook that wraps AuthContext and adds role helpers.
 */
export default function useAuth() {
  const ctx = useAuthContext()

  const hasRole = (...roles) => roles.includes(ctx.user?.role)

  const canCreate   = () => hasRole('admin', 'loader')
  const canApprove  = () => hasRole('admin', 'approver')
  const canAdmin    = () => hasRole('admin')

  const roleLabel = () => ROLE_LABELS[ctx.user?.role] ?? 'Sin rol'

  return { ...ctx, hasRole, canCreate, canApprove, canAdmin, roleLabel }
}
