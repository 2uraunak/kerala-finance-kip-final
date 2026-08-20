import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Dashboard() {
  const { authHeaders, user } = useAuthStore()
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recentDocs, setRecentDocs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [statsResp, docsResp] = await Promise.all([
          fetch('/api/v1/analytics/summary?days=30', { headers: authHeaders() }),
          fetch('/api/v1/documents/?limit=5', { headers: authHeaders() }),
        ])
        if (statsResp.ok) setStats(await statsResp.json())
        if (docsResp.ok) {
          const data = await docsResp.json()
          setRecentDocs(data.documents || [])
        }
      } catch (e) { /* service may not be up in dev */ }
      setLoading(false)
    }
    load()
  }, [])

  const STAT_CARDS = [
    { icon: '📄', label: 'Total Documents', value: stats?.total_documents ?? '—', color: '#c9a227' },
    { icon: '✅', label: 'Active Orders', value: stats?.active_documents ?? '—', color: '#22c55e' },
    { icon: '🔄', label: 'Superseded', value: stats?.superseded_documents ?? '—', color: '#ef4444' },
    { icon: '🔍', label: 'Searches (30d)', value: stats?.total_search_queries ?? '—', color: '#60a5fa' },
    { icon: '👥', label: 'Active Users', value: stats?.active_users ?? '—', color: '#a78bfa' },
    { icon: '🖨️', label: 'Scanned PDFs', value: stats?.scanned_documents ?? '—', color: '#fb923c' },
  ]

  const QUICK_ACTIONS = [
    { icon: '🔍', label: 'Search Documents', path: '/search', desc: 'Natural language Q&A with source citations' },
    { icon: '💹', label: 'GST Policy Assistant', path: '/gst', desc: 'Ask GST policy questions with circular references' },
    { icon: '✍️', label: 'Draft Policy Note', path: '/policy-agent', desc: 'AI-assisted multi-step policy note drafter' },
    { icon: '⚗️', label: 'Extract Clauses', path: '/extract', desc: 'Extract clauses and financial figures from GOs' },
    { icon: '🔗', label: 'Check Lineage', path: '/lineage', desc: 'Verify if a GO is active or superseded' },
    { icon: '📊', label: 'View Analytics', path: '/analytics', desc: 'Usage metrics and audit trail' },
  ]

  return (
    <div>
      {/* Welcome Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(201,162,39,0.1) 0%, rgba(17,24,39,0) 100%)',
        border: '1px solid var(--color-border-accent)',
        borderRadius: '16px',
        padding: '28px 32px',
        marginBottom: '32px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', right: 24, top: '50%', transform: 'translateY(-50%)',
          fontSize: '5rem', opacity: 0.08,
        }}>🏛️</div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '6px' }}>
          Welcome back, <span style={{ color: 'var(--color-accent)' }}>{user?.username}</span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
          Kerala Finance Department — Knowledge Intelligence Platform •
          <span style={{ color: 'var(--color-active)', marginLeft: 6 }}>● System Operational</span>
        </p>
        <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', background: 'rgba(34,197,94,0.1)', color: 'var(--color-active)', padding: '4px 10px', borderRadius: '999px', border: '1px solid rgba(34,197,94,0.2)' }}>
            🔒 Local Deployment
          </span>
          <span style={{ fontSize: '0.75rem', background: 'rgba(201,162,39,0.1)', color: 'var(--color-accent)', padding: '4px 10px', borderRadius: '999px', border: '1px solid var(--color-border-accent)' }}>
            🤖 Ollama LLM Active
          </span>
          <span style={{ fontSize: '0.75rem', background: 'rgba(96,165,250,0.1)', color: '#60a5fa', padding: '4px 10px', borderRadius: '999px', border: '1px solid rgba(96,165,250,0.2)' }}>
            🧠 Embeddings: sentence-transformers
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid-3 mb-xl">
        {STAT_CARDS.map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-icon">{s.icon}</div>
            <div className="stat-value" style={{ background: `linear-gradient(135deg, ${s.color}, ${s.color}99)`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              {loading ? '...' : s.value}
            </div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        {/* Quick Actions */}
        <div>
          <h3 style={{ marginBottom: '16px', color: 'var(--color-text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Quick Actions
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {QUICK_ACTIONS.map(a => (
              <div
                key={a.path}
                className="card"
                style={{ cursor: 'pointer', padding: '14px 16px', display: 'flex', alignItems: 'center', gap: '14px' }}
                onClick={() => navigate(a.path)}
              >
                <span style={{ fontSize: '1.5rem' }}>{a.icon}</span>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{a.label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{a.desc}</div>
                </div>
                <span style={{ marginLeft: 'auto', color: 'var(--color-text-muted)', fontSize: '1.1rem' }}>›</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Documents */}
        <div>
          <h3 style={{ marginBottom: '16px', color: 'var(--color-text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Recent Documents
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {loading ? (
              [...Array(4)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 60, borderRadius: '10px' }} />
              ))
            ) : recentDocs.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '32px' }}>
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📂</div>
                <p>No documents yet. Run <code>make seed</code> to load samples.</p>
              </div>
            ) : recentDocs.map(doc => (
              <div key={doc.id} className="card" style={{ padding: '12px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '0.83rem', fontWeight: 600, marginBottom: '4px', lineHeight: 1.4 }}>
                      {doc.title?.slice(0, 70)}{doc.title?.length > 70 ? '...' : ''}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                      {doc.doc_number} • {doc.year}
                    </div>
                  </div>
                  <span className={`badge badge-${doc.status}`}>{doc.status}</span>
                </div>
              </div>
            ))}
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/documents')}>
              View All Documents →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
