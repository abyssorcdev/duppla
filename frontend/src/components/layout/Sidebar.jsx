import { NavLink, useNavigate } from 'react-router-dom'
import useTheme from '../../hooks/useTheme'
import useAuth from '../../hooks/useAuth'

const ROLE_LABELS = { admin: 'Administrador', loader: 'Cargador', approver: 'Aprobador' }

export default function Sidebar() {
  const { isDark, toggle } = useTheme()
  const { user, logout, canAdmin } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const navLinks = [
    {
      to: '/',
      label: 'Dashboard',
      show: true,
      icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />,
    },
    {
      to: '/documents',
      label: 'Documentos',
      show: true,
      icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />,
    },
    {
      to: '/jobs',
      label: 'Jobs',
      show: true,
      icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />,
    },
    {
      to: '/admin',
      label: 'Administración',
      show: canAdmin(),
      icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />,
    },
  ]

  return (
    <aside className="w-64 min-h-screen bg-brand-900 text-white flex flex-col">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-brand-700 flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
            </svg>
          </div>
          <div>
            <span className="text-base font-bold tracking-tight text-white">Duppla</span>
            <p className="text-[10px] text-brand-400 leading-none mt-0.5">Gestión de Documentos</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navLinks.filter((l) => l.show).map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-700 text-white'
                  : 'text-brand-400 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {icon}
            </svg>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom: user info + theme + logout */}
      <div className="px-4 py-4 border-t border-white/10 space-y-3">
        {/* User card */}
        {user && (
          <div className="flex items-center gap-2.5 px-2">
            {user.picture ? (
              <img src={user.picture} alt="" className="w-8 h-8 rounded-full flex-shrink-0" />
            ) : (
              <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-semibold">
                  {user.name?.charAt(0)?.toUpperCase()}
                </span>
              </div>
            )}
            <div className="min-w-0">
              <p className="text-xs font-medium text-white truncate">{user.name}</p>
              <p className="text-[10px] text-brand-400 truncate">
                {ROLE_LABELS[user.role] || 'Sin rol'}
              </p>
            </div>
          </div>
        )}

        {/* Theme toggle */}
        <button
          onClick={toggle}
          title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-brand-400 hover:bg-white/5 hover:text-white transition-colors"
        >
          {isDark ? (
            <>
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 5a7 7 0 100 14A7 7 0 0012 5z" />
              </svg>
              <span>Modo claro</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <span>Modo oscuro</span>
            </>
          )}
        </button>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-brand-400 hover:bg-white/5 hover:text-red-400 transition-colors"
        >
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>
  )
}
