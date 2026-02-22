import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/auth/ProtectedRoute'
import useTheme from './hooks/useTheme'

// Public pages
import LoginPage from './pages/LoginPage'
import AuthCallbackPage from './pages/AuthCallbackPage'
import PendingApprovalPage from './pages/PendingApprovalPage'
import ForbiddenPage from './pages/ForbiddenPage'

// Protected pages
import DashboardPage from './pages/DashboardPage'
import DocumentsPage from './pages/DocumentsPage'
import DocumentCreatePage from './pages/DocumentCreatePage'
import DocumentDetailPage from './pages/DocumentDetailPage'
import JobsPage from './pages/JobsPage'
import JobPage from './pages/JobPage'
import AdminPage from './pages/AdminPage'

function AppRoutes() {
  useTheme()

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />
      <Route path="/pending" element={<PendingApprovalPage />} />
      <Route path="/403" element={<ForbiddenPage />} />

      {/* Protected — any active role */}
      <Route element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/documents/:id" element={<DocumentDetailPage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/jobs/:jobId" element={<JobPage />} />

        {/* loader + admin only */}
        <Route path="/documents/new" element={
          <ProtectedRoute roles={['admin', 'loader']}>
            <DocumentCreatePage />
          </ProtectedRoute>
        } />

        {/* admin only */}
        <Route path="/admin" element={
          <ProtectedRoute roles={['admin']}>
            <AdminPage />
          </ProtectedRoute>
        } />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
