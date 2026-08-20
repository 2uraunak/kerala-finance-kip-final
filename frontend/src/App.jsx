import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import SearchPage from './pages/SearchPage'
import DocumentsPage from './pages/DocumentsPage'
import LineagePage from './pages/LineagePage'
import ExtractionPage from './pages/ExtractionPage'
import GSTAssistant from './pages/GSTAssistant'
import PolicyNoteAgent from './pages/PolicyNoteAgent'
import Analytics from './pages/Analytics'
import Sidebar from './components/Sidebar'
import Header from './components/Header'

function ProtectedLayout({ children }) {
  const user = useAuthStore(s => s.user)
  const token = useAuthStore(s => s.token)
  if (!token || !user) return <Navigate to="/login" replace />
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-content">
        <Header />
        <main className="page-content">{children}</main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/search" element={<ProtectedLayout><SearchPage /></ProtectedLayout>} />
      <Route path="/documents" element={<ProtectedLayout><DocumentsPage /></ProtectedLayout>} />
      <Route path="/lineage" element={<ProtectedLayout><LineagePage /></ProtectedLayout>} />
      <Route path="/extract" element={<ProtectedLayout><ExtractionPage /></ProtectedLayout>} />
      <Route path="/gst" element={<ProtectedLayout><GSTAssistant /></ProtectedLayout>} />
      <Route path="/policy-agent" element={<ProtectedLayout><PolicyNoteAgent /></ProtectedLayout>} />
      <Route path="/analytics" element={<ProtectedLayout><Analytics /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
