import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

export default function LineagePage() {
  const { authHeaders } = useAuthStore()
  const [docId, setDocId] = useState('')
  const [docNumber, setDocNumber] = useState('')
  const [lineage, setLineage] = useState(null)
  const [activeVersion, setActiveVersion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [docs, setDocs] = useState([])

  useEffect(() => {
    fetch('/api/v1/documents/?limit=20', { headers: authHeaders() })
      .then(r => r.ok ? r.json() : null)
      .then(data => data && setDocs(data.documents || []))
  }, [])

  const checkLineage = async () => {
    if (!docId) return
    setLoading(true)
    try {
      const resp = await fetch(`/api/v1/lineage/${docId}`, { headers: authHeaders() })
      if (resp.ok) setLineage(await resp.json())
    } catch (e) {}
    setLoading(false)
  }

  const checkActive = async () => {
    if (!docNumber) return
    setLoading(true)
    try {
      const resp = await fetch(`/api/v1/lineage/active/${encodeURIComponent(docNumber)}`, { headers: authHeaders() })
      if (resp.ok) setActiveVersion(await resp.json())
    } catch (e) {}
    setLoading(false)
  }

  const renderNode = (node, depth = 0) => (
    <div key={node.id} style={{ marginLeft: depth * 24 }}>
      <div className={`lineage-node ${node.status}`} style={{ marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{node.title}</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
              {node.doc_number} • {node.issue_date || 'Date unknown'} • Depth: {node.depth}
            </div>
          </div>
          <span className={`badge badge-${node.status}`}>{node.status.toUpperCase()}</span>
        </div>
        {node.status === 'superseded' && (
          <div style={{ marginTop: 6, fontSize: '0.72rem', color: 'var(--color-superseded)' }}>
            ⚠️ This order has been superseded — do not cite for file processing
          </div>
        )}
      </div>
      {node.superseded_by?.map(child => (
        <div key={child.id}>
          <div className="lineage-connector" />
          <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textAlign: 'center', marginBottom: 4 }}>
            superseded by ↓
          </div>
          {renderNode(child, depth + 1)}
        </div>
      ))}
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h1>🔗 Document Lineage & Version Tracking</h1>
        <p>Trace Government Order supersession chains and find the currently active version</p>
      </div>

      <div className="grid-2 mb-xl">
        {/* Lineage by Doc ID */}
        <div className="card">
          <h4 style={{ marginBottom: '16px' }}>📜 Trace Lineage by Document</h4>
          <div className="input-group">
            <label className="input-label">Select Document</label>
            <select className="input" value={docId} onChange={e => setDocId(e.target.value)}>
              <option value="">— Select a document —</option>
              {docs.map(d => (
                <option key={d.id} value={d.id}>
                  {d.doc_number || d.id.slice(0, 8)} — {d.title?.slice(0, 50)}
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary btn-sm" onClick={checkLineage} disabled={loading || !docId}>
            {loading ? <span className="loading-spinner" style={{ width: 14, height: 14 }} /> : '🔗 Trace Lineage'}
          </button>
        </div>

        {/* Active Version by GO Number */}
        <div className="card">
          <h4 style={{ marginBottom: '16px' }}>✅ Find Active Version by GO Number</h4>
          <div className="input-group">
            <label className="input-label">GO Number (partial match)</label>
            <input className="input" value={docNumber} onChange={e => setDocNumber(e.target.value)}
              placeholder="e.g. GO(Ms)No.45" />
          </div>
          <button className="btn btn-primary btn-sm" onClick={checkActive} disabled={loading || !docNumber}>
            {loading ? <span className="loading-spinner" style={{ width: 14, height: 14 }} /> : '✅ Find Active Version'}
          </button>
        </div>
      </div>

      {/* Lineage Graph */}
      {lineage && (
        <div className="card mb-lg">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h4>Lineage Chain</h4>
            <span className={`badge badge-${lineage.current_status}`}>{lineage.current_status?.toUpperCase()}</span>
          </div>
          {lineage.is_superseded && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '8px', padding: '10px 14px', marginBottom: '16px',
              fontSize: '0.85rem', color: 'var(--color-superseded)',
            }}>
              ⚠️ <strong>Warning:</strong> This document is SUPERSEDED.
              Do not use it for file processing or policy citations without checking the superseding order.
            </div>
          )}
          {lineage.lineage_chain?.map(node => renderNode(node))}

          {/* Versions */}
          {lineage.versions?.length > 0 && (
            <div style={{ marginTop: '16px', borderTop: '1px solid var(--color-border)', paddingTop: '16px' }}>
              <h5 style={{ marginBottom: '8px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                All Versions ({lineage.versions.length})
              </h5>
              {lineage.versions.map((v, i) => (
                <div key={i} style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>
                  <span>v{v.version_number}</span>
                  <span>{v.change_summary || 'No summary'}</span>
                  <span>{v.created_at?.slice(0, 10)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Active Version Result */}
      {activeVersion && (
        <div className="card">
          <h4 style={{ marginBottom: '16px' }}>Active Version for "{docNumber}"</h4>
          {activeVersion.warning && (
            <div style={{ color: 'var(--color-superseded)', fontSize: '0.85rem', marginBottom: '12px' }}>
              ⚠️ {activeVersion.warning}
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {activeVersion.active_version ? (
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>✅ CURRENTLY ACTIVE</div>
                <div style={{ fontWeight: 600 }}>{activeVersion.active_version.title}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{activeVersion.active_version.doc_number}</div>
              </div>
            ) : (
              <div style={{ color: 'var(--color-superseded)' }}>No active version found</div>
            )}
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '4px' }}>Total Versions</div>
              <div style={{ fontWeight: 600, fontSize: '1.5rem' }}>{activeVersion.total_versions}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
