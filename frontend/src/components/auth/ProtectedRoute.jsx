import { Navigate, useLocation } from 'react-router-dom'
import useAuth from '../../hooks/useAuth'

/**
 * Wraps a route and enforces authentication + optional role check.
 *
 * Props:
 *   roles  — array of allowed roles, e.g. ['admin', 'loader']. If omitted,
 *            any active user is allowed.
 *   children — the protected page component.
 */
export default function ProtectedRoute({ roles, children }) {
  const { isAuthenticated, isPending, hasRole } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (isPending) {
    return <Navigate to="/pending" replace />
  }

  if (roles && !hasRole(...roles)) {
    return <Navigate to="/403" replace />
  }

  return children
}
