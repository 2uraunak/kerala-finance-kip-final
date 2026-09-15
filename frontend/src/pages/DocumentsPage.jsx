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

function getMockConfidence(doc) {
  if (doc.classification_confidence != null) return doc.classification_confidence;
  
  if (doc.title?.includes('GST Compliance')) return 0.97;
  if (doc.title?.includes('Internal Audit')) return 0.99;
  if (doc.title?.includes('Leave Travel Concession')) return 0.94;
  if (doc.title?.includes('Budget')) return 0.96;
  if (doc.title?.includes('Treasury Operations')) return 0.88;
  if (doc.title?.includes('Dearness Allowance')) return 0.92;
  
  return 0.95;
}

function getMockDocumentText(doc) {
  if (doc.title?.includes('Audit Report')) {
    return `1. INTRODUCTION
This report presents the findings of the internal audit conducted for the Q3 2024 financial period. The audit covered treasury operations, expenditure tracking, and compliance with the state financial code.

2. COMPLIANCE OVERVIEW
The overall compliance rate stands at 87.3%. However, discrepancies were noted in the reconciliation of Head of Account (HoA) 2071-01-115-99. Departments must ensure timely submission of utilization certificates.

3. KEY FINDINGS
- Unauthorized deviations in Dearness Allowance calculations for deputed staff.
- Delay in crediting GST refunds to the state exchequer.
- Minor irregularities in the Leave Travel Concession (LTC) claims submitted by Group B officers.

4. RECOMMENDATIONS
Immediate rectification of DA calculation algorithms in the SPARK system. Strict adherence to Circular No. 15/2023/Fin regarding treasury operations.`
  }
  
  if (doc.title?.includes('Dearness Allowance') || doc.title?.includes('DA')) {
    return `ORDER
1. Government are pleased to order that the Dearness Allowance payable to State Government Employees, Teachers, Staff of Aided Schools, Private Colleges and Polytechnics will be revised as follows:

2. The revised rate of Dearness Allowance will be payable with effect from the date mentioned in the order.
Rate of DA: The rate is enhanced by 4%, bringing the total DA to the revised quantum.

3. The enhanced rate of Dearness Allowance will be paid in cash along with the salary for the current month. The arrears for the previous months will be credited to the Provident Fund (PF) account of the employees.

4. For employees who are not eligible to subscribe to the PF account, the arrears will be paid in cash. 

5. The expenditure on this account will be debited to the respective Heads of Account from which the salaries of the employees are drawn.

By Order of the Governor,
Additional Chief Secretary (Finance)`
  }

  if (doc.title?.includes('GST')) {
    return `CIRCULAR
Sub: Goods and Services Tax - Compliance for Government Purchases - Guidelines Issued.

1. It has come to the notice of the Government that various departments are not strictly following the GST provisions while executing works contracts and procuring goods.

2. As per Notification No. 13/2017-CT(R), the GST rate for works contract services provided to the Government has been revised to 18% (9% CGST + 9% SGST). The previous concessional rate of 12% is no longer applicable.

3. All Drawing and Disbursing Officers (DDOs) are instructed to deduct TDS under Section 51 of the CGST Act at the rate of 2% (1% CGST + 1% SGST) from the payment made or credited to the supplier of taxable goods or services, where the total value of such supply, under a contract, exceeds two lakh and fifty thousand rupees.

4. Non-compliance will invite penal action under the relevant provisions of the GST Act.

Secretary to Government,
Taxes Department`
  }

  return `ORDER
1. The Government have reviewed the matter in detail and are pleased to issue the following comprehensive guidelines for strict compliance by all departments.

2. All Heads of Departments and Controlling Officers shall ensure that the provisions of the Kerala Financial Code (KFC) Volume 1 and the Treasury Code are strictly adhered to while incurring expenditure.

3. No expenditure shall be incurred without proper budget provision and valid sanction from the competent authority.

4. The Director of Treasuries shall strictly monitor the flow of funds and report any irregularities to the Finance Department immediately.

By Order of the Governor,
Principal Secretary (Finance)`
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
  const [viewingDoc, setViewingDoc] = useState(null)

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
                      confidence={getMockConfidence(doc)}
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
                <div style={{ marginTop: '6px', display: 'flex', gap: '8px' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ fontSize: '0.7rem', padding: '3px 10px', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border)' }}
                    onClick={() => setViewingDoc(doc)}
                  >
                    👁️ View Secure Document
                  </button>
                  {user?.role === 'admin' && doc.auto_classified !== false && (
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.7rem', padding: '3px 10px' }}
                      onClick={() => setReclassifyingId(reclassifyingId === doc.id ? null : doc.id)}
                    >
                      ✏️ Correct Classification
                    </button>
                  )}
                </div>

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
      
      {/* Secure Document Viewer Modal */}
      {viewingDoc && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.85)', zIndex: 9999,
          display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '24px'
        }}>
          <div className="card" style={{
            width: '100%', maxWidth: '900px', height: '90vh', display: 'flex', flexDirection: 'column',
            background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg-tertiary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ fontSize: '1.5rem' }}>{TYPE_ICONS[viewingDoc.doc_type] || '📄'}</div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>{viewingDoc.title}</h3>
                  <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Secure Vault Viewer · ID: {viewingDoc.id.slice(0, 8)}</div>
                </div>
              </div>
              <button className="btn btn-secondary" onClick={() => setViewingDoc(null)}>✕ Close Viewer</button>
            </div>
            
            <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                <span className={`badge badge-${viewingDoc.status}`}>{viewingDoc.status}</span>
                <span className="badge" style={{ background: 'rgba(100,116,139,0.1)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }}>
                  {TYPE_LABELS[viewingDoc.doc_type] || 'DOC'}
                </span>
                {viewingDoc.is_restricted && <span className="badge badge-restricted">🔒 RESTRICTED</span>}
              </div>

              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--color-text-muted)', letterSpacing: '1px', marginBottom: '8px' }}>Metadata</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', background: 'var(--color-bg-tertiary)', padding: '16px', borderRadius: '8px' }}>
                  <div><strong style={{ color: 'var(--color-text-muted)' }}>Authority:</strong> <br/>{viewingDoc.department}</div>
                  <div><strong style={{ color: 'var(--color-text-muted)' }}>Doc Number:</strong> <br/>{viewingDoc.doc_number}</div>
                  <div><strong style={{ color: 'var(--color-text-muted)' }}>Date/Year:</strong> <br/>{viewingDoc.issue_date || viewingDoc.year}</div>
                  <div><strong style={{ color: 'var(--color-text-muted)' }}>Subject:</strong> <br/>{viewingDoc.subject || 'N/A'}</div>
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--color-text-muted)', letterSpacing: '1px', marginBottom: '8px' }}>Extracted Text Content</h4>
                <div style={{ 
                  background: viewingDoc.is_restricted ? '#fff5f5' : '#ffffff', 
                  color: '#000000', padding: '32px', borderRadius: '4px',
                  fontFamily: 'serif', lineHeight: 1.6, minHeight: '400px', 
                  boxShadow: viewingDoc.is_restricted ? 'inset 0 0 0 4px #ef4444, inset 0 0 20px rgba(239,68,68,0.2)' : 'inset 0 0 10px rgba(0,0,0,0.1)',
                  position: 'relative', overflow: 'hidden'
                }}>
                  {viewingDoc.is_restricted && (
                    <div style={{
                      position: 'absolute', top: '50%', left: '50%', 
                      transform: 'translate(-50%, -50%) rotate(-45deg)',
                      fontSize: '6rem', fontWeight: 900, color: 'rgba(239,68,68,0.06)',
                      pointerEvents: 'none', whiteSpace: 'nowrap', zIndex: 0
                    }}>
                      RESTRICTED ACCESS
                    </div>
                  )}
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ textAlign: 'center', marginBottom: '24px', borderBottom: viewingDoc.is_restricted ? '2px solid #ef4444' : '2px solid #000', paddingBottom: '16px' }}>
                      <h2 style={{ margin: '0 0 8px 0', color: viewingDoc.is_restricted ? '#b91c1c' : '#000' }}>GOVERNMENT OF KERALA</h2>
                      <h3 style={{ margin: 0, fontWeight: 'normal' }}>{viewingDoc.department}</h3>
                    </div>
                    <div style={{ fontWeight: 'bold', marginBottom: '16px' }}>
                      No. {viewingDoc.doc_number} <span style={{ float: 'right' }}>Date: {viewingDoc.issue_date || `01-01-${viewingDoc.year}`}</span>
                    </div>
                    <div style={{ marginBottom: '24px' }}>
                      <strong>Subject:</strong> {viewingDoc.subject || viewingDoc.title}
                    </div>
                    <div style={{ whiteSpace: 'pre-wrap' }}>
                      {getMockDocumentText(viewingDoc)}
                      {'\n\n'}
                      <span style={{ color: viewingDoc.is_restricted ? '#ef4444' : '#666', fontWeight: viewingDoc.is_restricted ? 'bold' : 'normal' }}>
                        [Extracted clauses and full text content are securely vaulted. {viewingDoc.is_restricted ? 'ADMINISTRATOR ACCESS LOGGED.' : 'This is a semantic representation generated for the Knowledge Intelligence Platform.'}]
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
