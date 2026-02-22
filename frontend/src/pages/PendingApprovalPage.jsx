import { useNavigate } from 'react-router-dom'
import useAuth from '../hooks/useAuth'

export default function PendingApprovalPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-50 px-4">
      <div className="w-full max-w-md text-center">
        {/* Illustration */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-amber-100 mb-6">
          <svg className="w-10 h-10 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-2">Cuenta en revisión</h1>
        <p className="text-gray-500 text-sm mb-6 leading-relaxed">
          Tu cuenta ha sido registrada con el correo{' '}
          <span className="font-medium text-gray-700">{user?.email}</span>.
          <br />
          Un administrador debe aprobarla antes de que puedas acceder al sistema.
          Recibirás acceso tan pronto como se te asigne un rol.
        </p>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 mb-6 text-left space-y-3">
          <div className="flex items-center gap-3">
            {user?.picture && (
              <img src={user.picture} alt="" className="w-10 h-10 rounded-full" />
            )}
            <div>
              <p className="font-medium text-gray-800 text-sm">{user?.name}</p>
              <p className="text-gray-400 text-xs">{user?.email}</p>
            </div>
          </div>
          <div className="pt-2 border-t border-gray-100">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium bg-amber-50 text-amber-700 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              Esperando aprobación
            </span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="text-sm text-brand-700 hover:underline"
        >
          Cerrar sesión y usar otra cuenta
        </button>
      </div>
    </div>
  )
}
