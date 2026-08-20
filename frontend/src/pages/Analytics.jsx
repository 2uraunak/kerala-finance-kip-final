import { useEffect, useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Doughnut, Bar } from 'react-chartjs-2'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

export default function Analytics() {
  const { authHeaders } = useAuthStore()
  const [summary, setSummary] = useState(null)
  const [coverage, setCoverage] = useState(null)
  const [topQueries, setTopQueries] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [sResp, cResp, qResp, aResp] = await Promise.all([
          fetch('/api/v1/analytics/summary?days=30', { headers: authHeaders() }),
          fetch('/api/v1/analytics/document-coverage', { headers: authHeaders() }),
          fetch('/api/v1/analytics/top-queries?days=7&limit=8', { headers: authHeaders() }),
          fetch('/api/v1/analytics/audit-log?limit=15', { headers: authHeaders() }),
        ])
        if (sResp.ok) setSummary(await sResp.json())
        if (cResp.ok) setCoverage(await cResp.json())
        if (qResp.ok) setTopQueries((await qResp.json()).top_queries || [])
        if (aResp.ok) setAuditLogs((await aResp.json()).logs || [])
      } catch (e) {}
      setLoading(false)
    }
    load()
  }, [])

  const docTypeColors = ['#c9a227', '#22c55e', '#60a5fa', '#a78bfa', '#fb923c', '#34d399']

  const coverageChartData = coverage ? {
    labels: coverage.by_type?.map(t => t.doc_type?.replace('_', ' ').toUpperCase()) || [],
    datasets: [{
      data: coverage.by_type?.map(t => t.count) || [],
      backgroundColor: docTypeColors,
      borderColor: 'rgba(0,0,0,0)',
    }],
  } : null

  const topQueriesData = topQueries.length > 0 ? {
    labels: topQueries.map(q => (q.query || '').slice(0, 30)),
    datasets: [{
      label: 'Search Count',
      data: topQueries.map(q => q.count),
      backgroundColor: 'rgba(201,162,39,0.6)',
      borderColor: '#c9a227',
      borderWidth: 1,
      borderRadius: 4,
    }],
  } : null

  return (
    <div>
      <div className="page-header">
        <h1>📊 Analytics & Audit Trail</h1>
        <p>Platform usage metrics, document coverage, and enterprise audit log</p>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid-4 mb-xl">
          {[
            { icon: '📄', label: 'Total Documents', value: summary.total_documents },
            { icon: '🔍', label: 'Searches (30d)', value: summary.total_search_queries },
            { icon: '👥', label: 'Active Users', value: summary.active_users },
            { icon: '📊', label: 'Coverage', value: coverage ? `${coverage.coverage_percentage}%` : '—' },
          ].map(s => (
            <div key={s.label} className="stat-card">
              <div className="stat-icon">{s.icon}</div>
              <div className="stat-value">{loading ? '...' : s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid-2 mb-xl">
        {/* Document Coverage Chart */}
        <div className="card">
          <h4 style={{ marginBottom: '16px' }}>📂 Documents by Type</h4>
          {coverageChartData ? (
            <div style={{ maxWidth: 280, margin: '0 auto' }}>
              <Doughnut
                data={coverageChartData}
                options={{
                  plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
                  cutout: '65%',
                }}
              />
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '32px' }}>No data yet</div>
          )}
          {coverage && (
            <div style={{ marginTop: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '8px' }}>
                <span>Indexed Documents</span>
                <span style={{ color: 'var(--color-accent)', fontWeight: 700 }}>
                  {coverage.indexed_documents}/{coverage.total_documents} ({coverage.coverage_percentage}%)
                </span>
              </div>
              <div style={{ background: 'var(--color-bg-input)', borderRadius: '999px', height: 6, overflow: 'hidden' }}>
                <div style={{
                  width: `${coverage.coverage_percentage}%`,
                  height: '100%',
                  background: 'var(--gradient-accent)',
                  transition: 'width 1s ease',
                }} />
              </div>
            </div>
          )}
        </div>

        {/* Top Queries Chart */}
        <div className="card">
          <h4 style={{ marginBottom: '16px' }}>🔍 Top Queries (7 days)</h4>
          {topQueriesData ? (
            <Bar
              data={topQueriesData}
              options={{
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(30,45,68,0.8)' } },
                  y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                },
              }}
            />
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', padding: '32px' }}>
              No search queries yet
            </div>
          )}
        </div>
      </div>

      {/* Audit Log */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h4>🔒 Audit Trail (Last 15 Entries)</h4>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Append-only • Tamper-evident
          </span>
        </div>
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {[...Array(5)].map((_, i) => <div key={i} className="skeleton" style={{ height: 36 }} />)}
          </div>
        ) : auditLogs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-text-muted)' }}>
            No audit log entries yet
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                  {['Timestamp', 'User', 'Role', 'Action', 'Resource', 'Status', 'IP'].map(h => (
                    <th key={h} style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.3px' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(30,45,68,0.5)' }}>
                    <td style={{ padding: '8px 12px', color: 'var(--color-text-muted)' }}>{log.timestamp?.slice(0, 19)}</td>
                    <td style={{ padding: '8px 12px', fontWeight: 500 }}>{log.username || '—'}</td>
                    <td style={{ padding: '8px 12px' }}>
                      {log.role && <span className={`role-chip ${log.role}`}>{log.role}</span>}
                    </td>
                    <td style={{ padding: '8px 12px', color: 'var(--color-accent)', fontFamily: 'monospace', fontSize: '0.72rem' }}>{log.action}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--color-text-muted)' }}>{log.resource_type || '—'}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <span style={{ color: log.response_status?.startsWith('2') ? 'var(--color-active)' : 'var(--color-superseded)' }}>
                        {log.response_status}
                      </span>
                    </td>
                    <td style={{ padding: '8px 12px', color: 'var(--color-text-muted)', fontFamily: 'monospace', fontSize: '0.7rem' }}>{log.ip_address}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
