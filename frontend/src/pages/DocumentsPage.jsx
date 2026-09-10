import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

const TYPE_LABELS = {
  government_order: 'GO', circular: 'Circular', notification: 'Notification',
  office_memorandum: 'OM', budget_document: 'Budget', budget: 'Budget',
  gst_policy: 'GST', other: 'Other',
}
const TYPE_ICONS = {
  government_order: '📜', circular: '🔄', notification: '📢',
  office_memorandum: '📝', budget_document: '💰', budget: '💰',
  gst_policy: '💹', other: '📄',
}

function ClassificationBadge({ confidence, autoClassified }) {
  if (confidence == null) return null
  const pct = Math.round((confidence || 0) * 100)
  const color = pct >= 90 ? '#4ade80' : pct >= 75 ? '#fbbf24' : '#f87171'
  const bgColor = pct >= 90 ? 'rgba(74,222,128,0.1)' : pct >= 75 ? 'rgba(251,191,36,0.1)' : 'rgba(248,113,113,0.1)'
  return (
    <span
      title={autoClassified ? `Auto-classified with ${pct}% confidence` : 'Manually verified by administrator'}
      style={{
        fontSize: '0.62rem', fontWeight: 700, padding: '2px 7px',
        borderRadius: '999px', border: `1px solid ${color}`,
        background: bgColor, color, letterSpacing: '0.5px',
        cursor: 'default', userSelect: 'none',
      }}
    >
      {autoClassified ? `⚡ ${pct}%` : '✔ Verified'}
    </span>
  )
}

export default function DocumentsPage() {
  const { authHeaders, user } = useAuthStore()
  const [docs, setDocs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [docType, setDocType] = useState('')
  const [status, setStatus] = useState('')
  const [year, setYear] = useState('')
  const [subject, setSubject] = useState('')
  const [uploading, setUploading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadForm, setUploadForm] = useState({
    title: '', doc_number: '', doc_type: 'government_order', is_restricted: false,
  })
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const [reclassifyingId, setReclassifyingId] = useState(null)

  const loadDocs = async () => {
    setLoading(true)
    const params = new URLSearchParams({ limit: 50 })
    if (search) params.set('search', search)
    if (docType) params.set('doc_type', docType)
    if (status) params.set('status', status)
    if (year) params.set('year', year)
    try {
      const resp = await fetch(`/api/v1/documents/?${params}`, { headers: authHeaders() })
      if (resp.ok) {
        const data = await resp.json()
        setDocs(data.documents || [])
        setTotal(data.total || 0)
      }
    } catch (e) {}
    setLoading(false)
  }

  useEffect(() => { loadDocs() }, [search, docType, status, year, subject])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!uploadFile) return
    setUploading(true)
    setUploadResult(null)
    const form = new FormData()
    form.append('file', uploadFile)
    form.append('title', uploadForm.title)
    form.append('doc_number', uploadForm.doc_number)
    form.append('doc_type', uploadForm.doc_type)
    form.append('is_restricted', uploadForm.is_restricted)
    try {
      const resp = await fetch('/api/v1/documents/upload', {
        method: 'POST', headers: authHeaders(), body: form,
      })
      if (resp.ok) {
        const data = await resp.json()
        setUploadResult(data)
        setUploadFile(null)
        setUploadForm({ title: '', doc_number: '', doc_type: 'government_order', is_restricted: false })
        setTimeout(loadDocs, 2000)
      }
    } catch (e) {}
    setUploading(false)
  }

  const clearFilters = () => {
    setSearch(''); setDocType(''); setStatus(''); setYear(''); setSubject('')
  }
  const hasFilters = search || docType || status || year || subject

  const YEARS = [2020, 2021, 2022, 2023, 2024]

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>📂 Document Library</h1>
            <p>{total} documents indexed · Auto-classification active</p>
          </div>
          {(user?.role === 'admin' || user?.role === 'analyst') && (
            <button className="btn btn-primary" onClick={() => setShowUpload(!showUpload)}>
              ⬆️ Upload Document
            </button>
          )}
        </div>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <div className="card mb-lg" style={{ border: '1px solid var(--color-border-accent)' }}>
          <h4 style={{ marginBottom: '16px' }}>Upload New Document</h4>
          {uploadResult?.classification && (
            <div style={{
              padding: '12px 16px', borderRadius: '8px', marginBottom: '16px',
              background: 'rgba(74,222,128,0.08)', border: '1px solid rgba(74,222,128,0.3)',
            }}>
              <div style={{ fontWeight: 600, color: '#4ade80', marginBottom: '6px' }}>
                ⚡ Auto-Classification Result
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
                <span>Type: <strong>{uploadResult.classification.doc_type}</strong></span>
                <span>Confidence: <strong>{Math.round((uploadResult.classification.classification_confidence||0)*100)}%</strong></span>
                <span>Subject: <strong>{uploadResult.classification.subject || '—'}</strong></span>
                <span>Status: <strong>{uploadResult.classification.status}</strong></span>
              </div>
            </div>
          )}
          <form onSubmit={handleUpload}>
            <div className="grid-2">
              <div className="input-group">
                <label className="input-label">Document Title *</label>
                <input className="input" required value={uploadForm.title}
                  onChange={e => setUploadForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="Full title of the GO/Circular..." />
              </div>
              <div className="input-group">
                <label className="input-label">GO Number</label>
                <input className="input" value={uploadForm.doc_number}
                  onChange={e => setUploadForm(f => ({ ...f, doc_number: e.target.value }))}
                  placeholder="e.g. GO(Ms)No.45/2023/Fin" />
              </div>
            </div>
            <div className="grid-2">
              <div className="input-group">
                <label className="input-label">Document Type (will be auto-detected)</label>
                <select className="input" value={uploadForm.doc_type}
                  onChange={e => setUploadForm(f => ({ ...f, doc_type: e.target.value }))}>
                  <option value="government_order">Government Order</option>
                  <option value="circular">Circular</option>
                  <option value="notification">Notification</option>
                  <option value="office_memorandum">Office Memorandum</option>
                  <option value="budget_document">Budget Document</option>
                  <option value="gst_policy">GST Policy</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">PDF File *</label>
                <input className="input" type="file" accept=".pdf" required
                  onChange={e => setUploadFile(e.target.files[0])} />
              </div>
            </div>
            {user?.role === 'admin' && (
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', marginBottom: '16px', cursor: 'pointer' }}>
                <input type="checkbox" checked={uploadForm.is_restricted}
                  onChange={e => setUploadForm(f => ({ ...f, is_restricted: e.target.checked }))} />
                🔒 Mark as Restricted (Admin only access)
              </label>
            )}
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-primary" type="submit" disabled={uploading}>
                {uploading ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Uploading & Classifying...</> : '⬆️ Upload & Auto-Classify'}
              </button>
              <button className="btn btn-secondary" type="button" onClick={() => setShowUpload(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Filter Panel */}
      <div className="card mb-lg" style={{ padding: '16px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div className="search-bar" style={{ flex: 1, minWidth: 200 }}>
            <span>🔍</span>
            <input placeholder="Search by title..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <select className="input" style={{ width: 150 }} value={docType} onChange={e => setDocType(e.target.value)}>
            <option value="">All Types</option>
            <option value="government_order">Government Order</option>
            <option value="circular">Circular</option>
            <option value="notification">Notification</option>
            <option value="office_memorandum">Office Memo</option>
            <option value="budget_document">Budget</option>
            <option value="gst_policy">GST Policy</option>
          </select>
          <select className="input" style={{ width: 140 }} value={status} onChange={e => setStatus(e.target.value)}>
            <option value="">All Status</option>
            <option value="active">✅ Active</option>
            <option value="superseded">🔴 Superseded</option>
            <option value="draft">📝 Draft</option>
          </select>
          <select className="input" style={{ width: 110 }} value={year} onChange={e => setYear(e.target.value)}>
            <option value="">All Years</option>
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
          {hasFilters && (
            <button className="btn btn-secondary" onClick={clearFilters} style={{ fontSize: '0.78rem', padding: '6px 12px' }}>
              ✕ Clear
            </button>
          )}
        </div>
        {hasFilters && (
          <div style={{ marginTop: '8px', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Filtering: {[docType, status, year ? `Year: ${year}` : '', search].filter(Boolean).join(' · ')}
          </div>
        )}
      </div>

      {/* Document List */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton" style={{ height: 80 }} />)}
        </div>
      ) : docs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '64px', color: 'var(--color-text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📂</div>
          <p>
            {hasFilters
              ? `No documents match your current filters. Try adjusting the year, type, or status.`
              : `No documents found. Run `}{!hasFilters && <code style={{ color: 'var(--color-accent)' }}>make seed</code>}{!hasFilters && ` to load sample documents.`}
          </p>
          {hasFilters && (
            <button className="btn btn-secondary" onClick={clearFilters} style={{ marginTop: '12px' }}>
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {docs.map(doc => (
            <div key={doc.id} className="card" style={{
              display: 'flex', gap: '16px', alignItems: 'flex-start',
              borderLeft: doc.status === 'superseded' ? '3px solid var(--color-superseded, #ef4444)' : '3px solid transparent',
            }}>
              <div style={{ fontSize: '2rem', flexShrink: 0 }}>
                {TYPE_ICONS[doc.doc_type] || '📄'}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px', marginBottom: '6px' }}>
                  <div>
                    <h4 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: '2px' }}>{doc.title}</h4>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                      {doc.doc_number} · {doc.department || 'Finance Dept'} · {doc.year}
                      {doc.subject && ` · ${doc.subject}`}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '5px', flexShrink: 0, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    <span className={`badge badge-${doc.status}`}>{doc.status}</span>
                    {doc.is_restricted && <span className="badge badge-restricted">🔒 RESTRICTED</span>}
                    {doc.is_scanned && (
                      <span className="badge" style={{ background: 'rgba(96,165,250,0.1)', color: '#60a5fa', border: '1px solid rgba(96,165,250,0.3)' }}>
                        OCR
                      </span>
                    )}
                    <span className="badge" style={{ background: 'rgba(100,116,139,0.1)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)', fontSize: '0.65rem' }}>
                      {TYPE_LABELS[doc.doc_type] || 'DOC'}
                    </span>
                    <ClassificationBadge
                      confidence={doc.classification_confidence}
                      autoClassified={doc.auto_classified !== false}
                    />
                  </div>
                </div>

                {doc.summary && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                    {doc.summary?.slice(0, 160)}{doc.summary?.length > 160 ? '...' : ''}
                  </p>
                )}

                {/* Superseded warning */}
                {doc.status === 'superseded' && (
                  <div style={{
                    marginTop: '8px', padding: '6px 10px', borderRadius: '6px',
                    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                    fontSize: '0.75rem', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '6px',
                  }}>
                    🚫 <strong>SUPERSEDED:</strong>&nbsp;This order is no longer authoritative. Do not cite in policy notes.
                    {doc.superseded_by_id && <span style={{ opacity: 0.7 }}>→ Active version exists</span>}
                  </div>
                )}

                {/* Admin reclassify button */}
                {user?.role === 'admin' && doc.auto_classified !== false && (
                  <div style={{ marginTop: '6px' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.7rem', padding: '3px 10px' }}
                      onClick={() => setReclassifyingId(reclassifyingId === doc.id ? null : doc.id)}
                    >
                      ✏️ Correct Classification
                    </button>
                  </div>
                )}

                {/* Inline reclassify form */}
                {reclassifyingId === doc.id && (
                  <ReclassifyForm
                    doc={doc}
                    authHeaders={authHeaders}
                    onDone={() => { setReclassifyingId(null); loadDocs() }}
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ReclassifyForm({ doc, authHeaders, onDone }) {
  const [form, setForm] = useState({
    doc_type: doc.doc_type || 'government_order',
    subject: doc.subject || '',
    status: doc.status || 'active',
    reason: '',
  })
  const [saving, setSaving] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const resp = await fetch(`/api/v1/documents/${doc.id}/reclassify`, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (resp.ok) {
        setResult(await resp.json())
        setTimeout(onDone, 1500)
      }
    } catch (e) {}
    setSaving(false)
  }

  return (
    <form onSubmit={handleSubmit} style={{
      marginTop: '10px', padding: '12px', borderRadius: '8px',
      background: 'rgba(251,191,36,0.07)', border: '1px solid rgba(251,191,36,0.3)',
    }}>
      <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#fbbf24', marginBottom: '8px' }}>
        ✏️ Correct Classification (Admin)
      </div>
      {result ? (
        <div style={{ color: '#4ade80', fontSize: '0.8rem' }}>✅ Reclassified successfully!</div>
      ) : (
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <select className="input" style={{ flex: 1, minWidth: 130, fontSize: '0.8rem' }} value={form.doc_type} onChange={e => setForm(f => ({ ...f, doc_type: e.target.value }))}>
            <option value="government_order">Government Order</option>
            <option value="circular">Circular</option>
            <option value="notification">Notification</option>
            <option value="office_memorandum">Office Memo</option>
            <option value="budget_document">Budget</option>
            <option value="gst_policy">GST Policy</option>
          </select>
          <select className="input" style={{ flex: 1, minWidth: 110, fontSize: '0.8rem' }} value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))}>
            <option value="active">Active</option>
            <option value="superseded">Superseded</option>
            <option value="draft">Draft</option>
          </select>
          <input className="input" style={{ flex: 2, minWidth: 160, fontSize: '0.8rem' }} placeholder="Reason for correction..." required value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))} />
          <button className="btn btn-primary" type="submit" disabled={saving} style={{ fontSize: '0.78rem' }}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button className="btn btn-secondary" type="button" onClick={onDone} style={{ fontSize: '0.78rem' }}>Cancel</button>
        </div>
      )}
    </form>
  )
}
