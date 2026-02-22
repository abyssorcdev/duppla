import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import useAuth from '../hooks/useAuth'

/**
 * Landing page after Google OAuth redirect.
 * Reads ?token=... and ?status=... from the URL, stores the token,
 * then routes the user to the appropriate page.
 */
export default function AuthCallbackPage() {
  const [params] = useSearchParams()
  const { login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const token  = params.get('token')
    const status = params.get('status')
    const error  = params.get('error')

    if (error || !token) {
      navigate('/login?error=auth_failed', { replace: true })
      return
    }

    login(token)

    if (status === 'pending') {
      navigate('/pending', { replace: true })
    } else {
      navigate('/', { replace: true })
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-50">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 rounded-full border-4 border-brand-100 border-t-brand-700 animate-spin" />
        <p className="text-sm text-brand-600">Iniciando sesión...</p>
      </div>
    </div>
  )
}
