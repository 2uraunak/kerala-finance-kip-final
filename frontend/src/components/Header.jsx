import { useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const PAGE_TITLES = {
  '/': 'Dashboard — Overview',
  '/search': 'Search Documents',
  '/documents': 'Document Library',
  '/lineage': 'Lineage & Version Tracking',
  '/extract': 'Clause & Figure Extraction',
  '/gst': 'GST Policy Assistant',
  '/policy-agent': 'Policy Note Drafter Agent',
  '/analytics': 'Analytics & Audit Trail',
}

export default function Header() {
  const location = useLocation()
  const user = useAuthStore(s => s.user)
  const title = PAGE_TITLES[location.pathname] || 'Kerala Finance KIP'

  return (
    <header className="header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: 8, height: 8,
          borderRadius: '50%',
          background: 'var(--color-active)',
          boxShadow: '0 0 8px var(--color-active)',
          animation: 'pulse 2s infinite',
        }} />
        <span className="header-title">{title}</span>
      </div>

      <div className="header-user">
        <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
          🔒 Local Deploy • All data stays on-premise
        </div>
        <div className="user-badge">
          <span style={{ fontSize: '0.85rem' }}>👤</span>
          <span style={{ fontSize: '0.82rem', fontWeight: 500 }}>{user?.username}</span>
          <span className={`role-chip ${user?.role}`}>{user?.role}</span>
        </div>
      </div>
    </header>
  )
}
