import { Link } from 'react-router-dom'

export default function ForbiddenPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-full py-20 text-center px-4">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-gray-800 mb-2">Sin permisos</h1>
      <p className="text-gray-500 text-sm mb-6 max-w-sm">
        No tienes el rol necesario para acceder a esta sección.
        Contacta a un administrador si crees que es un error.
      </p>
      <Link to="/" className="text-sm text-brand-700 hover:underline">
        Volver al inicio
      </Link>
    </div>
  )
}
