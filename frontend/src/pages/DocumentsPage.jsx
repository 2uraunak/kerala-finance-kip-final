import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

export default function DocumentsPage() {
  const { authHeaders, user } = useAuthStore()
  const [docs, setDocs] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [docType, setDocType] = useState('')
  const [status, setStatus] = useState('')
  const [uploading, setUploading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [uploadForm, setUploadForm] = useState({ title: '', doc_number: '', doc_type: 'government_order', is_restricted: false })
  const [uploadFile, setUploadFile] = useState(null)

  const loadDocs = async () => {
    setLoading(true)
    const params = new URLSearchParams({ limit: 20 })
    if (search) params.set('search', search)
    if (docType) params.set('doc_type', docType)
    if (status) params.set('status', status)
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

  useEffect(() => { loadDocs() }, [search, docType, status])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!uploadFile) return
    setUploading(true)
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
        setShowUpload(false)
        setUploadFile(null)
        setUploadForm({ title: '', doc_number: '', doc_type: 'government_order', is_restricted: false })
        setTimeout(loadDocs, 2000)
      }
    } catch (e) {}
    setUploading(false)
  }

  const TYPE_LABELS = {
    government_order: 'GO', circular: 'Circular', notification: 'Notification',
    office_memorandum: 'OM', budget: 'Budget', gst_policy: 'GST', other: 'Other',
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>📂 Document Library</h1>
            <p>{total} documents indexed across all categories</p>
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
                <label className="input-label">Document Type</label>
                <select className="input" value={uploadForm.doc_type}
                  onChange={e => setUploadForm(f => ({ ...f, doc_type: e.target.value }))}>
                  <option value="government_order">Government Order</option>
                  <option value="circular">Circular</option>
                  <option value="notification">Notification</option>
                  <option value="office_memorandum">Office Memorandum</option>
                  <option value="budget">Budget</option>
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
                Mark as Restricted (Admin only access)
              </label>
            )}
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-primary" type="submit" disabled={uploading}>
                {uploading ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Uploading...</> : '⬆️ Upload & Ingest'}
              </button>
              <button className="btn btn-secondary" type="button" onClick={() => setShowUpload(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div className="search-bar" style={{ flex: 1, minWidth: 200 }}>
          <span>🔍</span>
          <input placeholder="Search by title..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input" style={{ width: 160 }} value={docType} onChange={e => setDocType(e.target.value)}>
          <option value="">All Types</option>
          <option value="government_order">Government Order</option>
          <option value="circular">Circular</option>
          <option value="gst_policy">GST Policy</option>
          <option value="budget">Budget</option>
          <option value="office_memorandum">Office Memo</option>
        </select>
        <select className="input" style={{ width: 140 }} value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="superseded">Superseded</option>
          <option value="draft">Draft</option>
        </select>
      </div>

      {/* Document List */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton" style={{ height: 80 }} />)}
        </div>
      ) : docs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '64px', color: 'var(--color-text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📂</div>
          <p>No documents found. Run <code style={{ color: 'var(--color-accent)' }}>make seed</code> to load sample documents.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {docs.map(doc => (
            <div key={doc.id} className="card" style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{ fontSize: '2rem', flexShrink: 0 }}>
                {{ government_order: '📜', circular: '🔄', notification: '📢', office_memorandum: '📝', budget: '💰', gst_policy: '💹', other: '📄' }[doc.doc_type] || '📄'}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px', marginBottom: '6px' }}>
                  <div>
                    <h4 style={{ fontSize: '0.92rem', fontWeight: 600, marginBottom: '2px' }}>{doc.title}</h4>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                      {doc.doc_number} • {doc.department} • {doc.year}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
                    <span className={`badge badge-${doc.status}`}>{doc.status}</span>
                    {doc.is_restricted && <span className="badge badge-restricted">🔒 RESTRICTED</span>}
                    {doc.is_scanned && <span className="badge" style={{ background: 'rgba(96,165,250,0.1)', color: '#60a5fa', border: '1px solid rgba(96,165,250,0.3)' }}>OCR</span>}
                    <span className="badge" style={{ background: 'rgba(100,116,139,0.1)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)', fontSize: '0.65rem' }}>
                      {TYPE_LABELS[doc.doc_type] || 'DOC'}
                    </span>
                  </div>
                </div>
                {doc.summary && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                    {doc.summary?.slice(0, 150)}{doc.summary?.length > 150 ? '...' : ''}
                  </p>
                )}
                {doc.status === 'superseded' && doc.superseded_by_id && (
                  <div style={{ marginTop: '6px', fontSize: '0.72rem', color: 'var(--color-superseded)' }}>
                    ⚠️ Superseded — do not use for file processing
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
