import { useState } from 'react'
import { useAuthStore } from '../store/authStore'

const EXAMPLE_QUERIES = [
  'What is the current Dearness Allowance rate for Kerala state employees?',
  'Has GO(Ms) No.45/2023 been superseded?',
  'What are the austerity measures for 2024-25?',
  'Show GST rate for works contract services to government',
  'What is the total budget allocation for education in 2024-25?',
]

export default function SearchPage() {
  const { authHeaders } = useAuthStore()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [includeSuperseded, setIncludeSuperseded] = useState(false)

  const doSearch = async (q = query) => {
    if (!q.trim()) return
    setLoading(true)
    setResults(null)
    try {
      const params = new URLSearchParams({
        q,
        top_k: 5,
        generate_answer: true,
        include_superseded: includeSuperseded,
      })
      const resp = await fetch(`/api/v1/search/?${params}`, { headers: authHeaders() })
      if (resp.ok) setResults(await resp.json())
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1>🔍 Search Government Documents</h1>
        <p>Natural language search with source citations and lineage verification</p>
      </div>

      {/* Search Bar */}
      <div style={{
        background: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        borderRadius: '16px',
        padding: '24px',
        marginBottom: '24px',
      }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
          <div className="search-bar" style={{ flex: 1 }}>
            <span>🔍</span>
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && doSearch()}
              placeholder="Ask anything about Kerala Finance Department orders, circulars, or GST policies..."
            />
          </div>
          <button className="btn btn-primary" onClick={() => doSearch()} disabled={loading}>
            {loading ? <span className="loading-spinner" /> : 'Search'}
          </button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--color-text-muted)', cursor: 'pointer' }}>
            <input type="checkbox" checked={includeSuperseded} onChange={e => setIncludeSuperseded(e.target.checked)} />
            Include superseded orders
          </label>
          <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>Try:</span>
          {EXAMPLE_QUERIES.map(q => (
            <button key={q} style={{
              background: 'var(--color-bg-input)', border: '1px solid var(--color-border)',
              borderRadius: '999px', padding: '4px 12px', fontSize: '0.72rem',
              color: 'var(--color-text-muted)', cursor: 'pointer',
            }}
              onClick={() => { setQuery(q); doSearch(q) }}
            >
              {q.slice(0, 40)}...
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '48px', color: 'var(--color-text-muted)' }}>
          <div className="loading-spinner" style={{ width: 32, height: 32, margin: '0 auto 12px' }} />
          <p>Searching documents and generating answer...</p>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div>
          {/* AI Answer */}
          {results.answer && (
            <div style={{
              background: 'linear-gradient(135deg, rgba(201,162,39,0.08), rgba(17,24,39,0))',
              border: '1px solid var(--color-border-accent)',
              borderRadius: '16px', padding: '24px', marginBottom: '20px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <span style={{ fontSize: '1.25rem' }}>🤖</span>
                <h3 style={{ fontSize: '1rem' }}>AI-Generated Answer</h3>
                <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                  Confidence: <span className={`confidence-${results.confidence > 0.6 ? 'HIGH' : 'MEDIUM'}`}>
                    {results.confidence > 0.6 ? 'HIGH' : 'MEDIUM'}
                  </span>
                </span>
              </div>
              <p style={{ color: 'var(--color-text-primary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                {results.answer}
              </p>
            </div>
          )}

          {/* Source Citations */}
          {results.citations?.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>
                📚 Source Review Labels ({results.citations.length})
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {results.citations.map((c, i) => (
                  <div key={i} className="source-label">
                    <span>{c.source_label}</span>
                    <span className={`badge badge-${c.status_label?.toLowerCase()}`}>{c.status_label}</span>
                    <span className={`confidence confidence-${c.confidence}`}>{c.confidence}</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>
                      [{c.match_type}] score: {c.relevance_score}
                    </span>
                    {c.lineage_warning && (
                      <span style={{ color: 'var(--color-superseded)', fontSize: '0.65rem', fontWeight: 700 }}>
                        ⚠️ SUPERSEDED
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Results */}
          <h4 style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '12px' }}>
            📄 Retrieved Chunks ({results.result_count})
            &nbsp;• Search types: {results.search_types_used?.join(', ')}
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {results.results?.map((r, i) => {
              const meta = r.metadata || {}
              return (
                <div key={i} className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-accent)' }}>
                      #{r.final_rank} — {meta.doc_title || 'Unknown'}
                    </div>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>Page {meta.page}</span>
                      <span className={`badge badge-${(meta.status || 'active')}`}>{(meta.status || 'active').toUpperCase()}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                        {r.match_type} • {r.rrf_score?.toFixed(4)}
                      </span>
                    </div>
                  </div>
                  <p style={{ fontSize: '0.83rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                    {r.chunk_text?.slice(0, 400)}{r.chunk_text?.length > 400 ? '...' : ''}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {!results && !loading && (
        <div style={{ textAlign: 'center', padding: '64px', color: 'var(--color-text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🔍</div>
          <p>Enter a question or keyword to search across all Kerala Finance documents</p>
        </div>
      )}
    </div>
  )
}
