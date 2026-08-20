import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const NAV_ITEMS = [
  { path: '/', icon: '🏠', label: 'Dashboard', section: 'Main' },
  { path: '/search', icon: '🔍', label: 'Search Documents', section: 'Search & Retrieval' },
  { path: '/documents', icon: '📂', label: 'Document Library', section: 'Search & Retrieval' },
  { path: '/lineage', icon: '🔗', label: 'Lineage & Versions', section: 'Document Intelligence' },
  { path: '/extract', icon: '⚗️', label: 'Extract Clauses & Figures', section: 'Document Intelligence' },
  { path: '/gst', icon: '💹', label: 'GST Policy Assistant', section: 'AI Assistance' },
  { path: '/policy-agent', icon: '✍️', label: 'Policy Note Agent', section: 'AI Assistance' },
  { path: '/analytics', icon: '📊', label: 'Analytics & Audit', section: 'Governance' },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const sections = [...new Set(NAV_ITEMS.map(i => i.section))]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{ fontSize: '1.5rem' }}>🏛️</span>
          <div>
            <div className="logo-title">Kerala Finance KIP</div>
            <div className="logo-subtitle">Knowledge Intelligence Platform</div>
          </div>
        </div>
        <div style={{
          fontSize: '0.68rem',
          color: 'var(--color-text-muted)',
          borderTop: '1px solid var(--color-border)',
          paddingTop: '8px',
          marginTop: '4px',
        }}>
          Finance Department, Govt. of Kerala
        </div>
      </div>

      {/* Navigation */}
      <div className="sidebar-nav">
        {sections.map(section => (
          <div key={section}>
            <div className="nav-section-label">{section}</div>
            {NAV_ITEMS.filter(i => i.section === section).map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      {/* User Footer */}
      <div style={{ padding: '16px', borderTop: '1px solid var(--color-border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <div style={{
            width: 32, height: 32,
            background: 'var(--gradient-accent)',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.8rem', fontWeight: 700, color: '#1a0f00',
          }}>
            {user?.username?.[0]?.toUpperCase() || '?'}
          </div>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{user?.username}</div>
            <span className={`role-chip ${user?.role}`}>{user?.role}</span>
          </div>
        </div>
        <button className="btn btn-secondary btn-sm w-full" onClick={handleLogout}
          style={{ justifyContent: 'center' }}>
          🚪 Logout
        </button>
      </div>
    </nav>
  )
}
