import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

export default function ExtractionPage() {
  const { authHeaders } = useAuthStore()
  const [docs, setDocs] = useState([])
  const [selectedDoc, setSelectedDoc] = useState('')
  const [extractType, setExtractType] = useState('full')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/v1/documents/?limit=20', { headers: authHeaders() })
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setDocs(d.documents || []))
  }, [])

  const doExtract = async () => {
    if (!selectedDoc) return
    setLoading(true)
    setResult(null)
    try {
      const resp = await fetch(`/api/v1/extract/${extractType}/${selectedDoc}`, {
        method: extractType === 'tables' ? 'GET' : 'POST',
        headers: authHeaders(),
      })
      if (resp.ok) setResult(await resp.json())
    } catch (e) {}
    setLoading(false)
  }

  const selectedDocObj = docs.find(d => d.id === selectedDoc)

  return (
    <div>
      <div className="page-header">
        <h1>⚗️ Clause & Figure Extraction</h1>
        <p>AI-powered extraction of structured clauses, financial figures, and tables from Government Orders</p>
      </div>

      {/* Controls */}
      <div className="card mb-lg">
        <div className="grid-2">
          <div className="input-group">
            <label className="input-label">Select Document</label>
            <select className="input" value={selectedDoc} onChange={e => setSelectedDoc(e.target.value)}>
              <option value="">— Select a document —</option>
              {docs.map(d => (
                <option key={d.id} value={d.id}>
                  {d.doc_number || d.id.slice(0, 8)} — {d.title?.slice(0, 55)}
                </option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Extraction Type</label>
            <select className="input" value={extractType} onChange={e => setExtractType(e.target.value)}>
              <option value="full">Full Extraction (Clauses + Figures + Entities)</option>
              <option value="clauses">Clauses Only</option>
              <option value="figures">Financial Figures Only</option>
              <option value="tables">Tables Only</option>
            </select>
          </div>
        </div>
        <button className="btn btn-primary" onClick={doExtract} disabled={!selectedDoc || loading}>
          {loading ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Extracting with AI...</> : '⚗️ Extract'}
        </button>
      </div>

      {/* Source Label */}
      {selectedDocObj && (
        <div className="source-label mb-lg">
          📄 <strong>{selectedDocObj.title?.slice(0, 60)}</strong>
          <span className={`badge badge-${selectedDocObj.status}`}>{selectedDocObj.status}</span>
          <span className="text-muted text-xs">{selectedDocObj.doc_number}</span>
        </div>
      )}

      {/* Results */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <div className="loading-spinner" style={{ width: 32, height: 32, margin: '0 auto 12px' }} />
          <p style={{ color: 'var(--color-text-muted)' }}>Sending to local LLM for structured extraction...</p>
        </div>
      )}

      {result && !loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Source Review Label */}
          <div style={{
            display: 'flex', gap: '16px', padding: '12px 16px',
            background: 'rgba(201,162,39,0.06)', border: '1px solid var(--color-border-accent)',
            borderRadius: '10px', fontSize: '0.8rem', alignItems: 'center', flexWrap: 'wrap',
          }}>
            <span>📊 <strong>Source Review Label</strong></span>
            <span>{result.source_label}</span>
            <span className={`badge badge-active`}>ACTIVE</span>
            <span style={{ color: 'var(--color-text-muted)' }}>Model: {result.model_used}</span>
            <span style={{ marginLeft: 'auto' }}>
              Confidence: <span className={`confidence confidence-${result.confidence}`}>{result.confidence}</span>
            </span>
          </div>

          {/* Clauses */}
          {result.clauses?.length > 0 && (
            <div>
              <h4 style={{ marginBottom: '12px' }}>📋 Extracted Clauses ({result.clause_count})</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {result.clauses.map((c, i) => (
                  <div key={i} className="card" style={{ borderLeft: '3px solid var(--color-accent)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, color: 'var(--color-accent)', fontSize: '0.85rem' }}>
                          Clause {c.clause_number}
                        </span>
                        <span className="badge" style={{ background: 'rgba(96,165,250,0.1)', color: '#60a5fa', border: '1px solid rgba(96,165,250,0.3)', fontSize: '0.62rem' }}>
                          {c.clause_type}
                        </span>
                      </div>
                      {c.page_reference && (
                        <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>Page {c.page_reference}</span>
                      )}
                    </div>
                    <p style={{ fontSize: '0.83rem', color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
                      {c.clause_text}
                    </p>
                    {c.key_entities?.length > 0 && (
                      <div style={{ marginTop: '6px', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {c.key_entities.map((e, ei) => (
                          <span key={ei} style={{ fontSize: '0.67rem', background: 'var(--color-bg-input)', padding: '2px 8px', borderRadius: '999px', color: 'var(--color-text-muted)' }}>
                            {e}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Figures */}
          {result.figures?.length > 0 && (
            <div>
              <h4 style={{ marginBottom: '12px' }}>💰 Financial Figures ({result.figure_count})</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                {result.figures.map((f, i) => (
                  <div key={i} className="card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--color-accent)', textTransform: 'uppercase', fontWeight: 700 }}>
                        {f.figure_type}
                      </span>
                      {f.page_reference && <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>p.{f.page_reference}</span>}
                    </div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '4px' }}>{f.value}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)' }}>{f.description}</div>
                    {f.context && (
                      <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: '4px', fontStyle: 'italic' }}>
                        "{f.context?.slice(0, 100)}..."
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.clauses?.length === 0 && result.figures?.length === 0 && (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--color-text-muted)' }}>
              <p>No structured data extracted. The document may need better OCR quality or the LLM may not have found structured content.</p>
            </div>
          )}
        </div>
      )}

      {!result && !loading && (
        <div style={{ textAlign: 'center', padding: '64px', color: 'var(--color-text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '12px' }}>⚗️</div>
          <p>Select a document and extraction type to extract structured data using the local AI model</p>
        </div>
      )}
    </div>
  )
}
