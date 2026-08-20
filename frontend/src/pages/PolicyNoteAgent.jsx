import { useState } from 'react'
import { useAuthStore } from '../store/authStore'

export default function PolicyNoteAgent() {
  const { authHeaders } = useAuthStore()
  const [subject, setSubject] = useState('')
  const [context, setContext] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(0)

  const EXAMPLE_SUBJECTS = [
    'Revision of Dearness Allowance for State Government Employees',
    'Implementation of GST compliance measures in Finance Department',
    'Austerity measures for capital expenditure in 2025-26',
  ]

  const draftNote = async () => {
    if (!subject.trim()) return
    setLoading(true)
    setResult(null)
    setActiveStep(0)
    try {
      const resp = await fetch('/api/v1/agent/draft-policy-note', {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, context }),
      })
      if (resp.ok) {
        const data = await resp.json()
        setResult(data)
        setActiveStep(data.agent_steps?.length || 0)
      }
    } catch (e) {}
    setLoading(false)
  }

  return (
    <div>
      <div className="page-header">
        <h1>✍️ Policy Note Drafter Agent</h1>
        <p>Multi-step AI agent: retrieves relevant GOs → verifies lineage → drafts policy note with citations</p>
      </div>

      {/* Input Form */}
      <div className="card mb-lg">
        <h4 style={{ marginBottom: '16px' }}>New Policy Note Request</h4>
        <div className="input-group">
          <label className="input-label">Subject *</label>
          <input className="input" value={subject} onChange={e => setSubject(e.target.value)}
            placeholder="e.g. Revision of Dearness Allowance for State Government Employees" />
        </div>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
          {EXAMPLE_SUBJECTS.map(s => (
            <button key={s} style={{
              background: 'var(--color-bg-input)', border: '1px solid var(--color-border)',
              borderRadius: '999px', padding: '4px 12px', fontSize: '0.72rem',
              color: 'var(--color-text-muted)', cursor: 'pointer',
            }} onClick={() => setSubject(s)}>{s.slice(0, 50)}...</button>
          ))}
        </div>
        <div className="input-group">
          <label className="input-label">Additional Context (optional)</label>
          <textarea className="input" rows={3} value={context} onChange={e => setContext(e.target.value)}
            placeholder="Any specific requirements, departments involved, effective date, etc." />
        </div>
        <button className="btn btn-primary" onClick={draftNote} disabled={!subject.trim() || loading}>
          {loading
            ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Agent working...</>
            : '🤖 Draft Policy Note'
          }
        </button>
      </div>

      {/* Agent Steps Visualization */}
      {(loading || result) && (
        <div className="card mb-lg">
          <h4 style={{ marginBottom: '16px' }}>🤖 Agent Execution Steps</h4>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            {[
              { step: 1, label: 'Retrieve Documents', icon: '🔍' },
              { step: 2, label: 'Verify Lineage', icon: '🔗' },
              { step: 3, label: 'Draft Note', icon: '✍️' },
            ].map(s => (
              <div key={s.step} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '8px 16px', borderRadius: '999px',
                  background: activeStep >= s.step ? 'rgba(34,197,94,0.15)' : (loading && activeStep === s.step - 1 ? 'rgba(201,162,39,0.15)' : 'var(--color-bg-input)'),
                  border: `1px solid ${activeStep >= s.step ? 'rgba(34,197,94,0.4)' : (loading && activeStep === s.step - 1 ? 'var(--color-border-accent)' : 'var(--color-border)')}`,
                  fontSize: '0.82rem', fontWeight: 500,
                  color: activeStep >= s.step ? 'var(--color-active)' : 'var(--color-text-muted)',
                  transition: 'all 0.4s ease',
                }}>
                  {loading && activeStep === s.step - 1 ? <span className="loading-spinner" style={{ width: 12, height: 12 }} /> : s.icon}
                  {s.label}
                </div>
                {s.step < 3 && <span style={{ color: 'var(--color-text-muted)' }}>→</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Policy Note Draft */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h4>📄 Policy Note Draft</h4>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => {
                  const el = document.createElement('a')
                  el.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(result.policy_note_draft)
                  el.download = `policy_note_${subject.slice(0, 20).replace(/ /g,'_')}.txt`
                  el.click()
                }}>⬇️ Download</button>
              </div>
            </div>
            <div style={{
              background: 'var(--color-bg-input)',
              border: '1px solid var(--color-border)',
              borderRadius: '8px', padding: '20px',
              fontFamily: 'monospace', fontSize: '0.83rem', lineHeight: 1.7,
              color: 'var(--color-text-primary)', whiteSpace: 'pre-wrap',
              maxHeight: '500px', overflowY: 'auto',
            }}>
              {result.policy_note_draft}
            </div>

            {/* Disclaimer */}
            <div style={{
              marginTop: '12px',
              background: 'rgba(245,158,11,0.08)',
              border: '1px solid rgba(245,158,11,0.3)',
              borderRadius: '8px', padding: '10px 14px',
              fontSize: '0.78rem', color: 'var(--color-draft)',
            }}>
              ⚠️ {result.disclaimer}
            </div>
          </div>

          {/* Source Citations */}
          {result.citations?.length > 0 && (
            <div className="card">
              <h4 style={{ marginBottom: '12px' }}>📚 Source Review Labels ({result.citations.length})</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {result.citations.map((c, i) => (
                  <div key={i} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 14px',
                    background: c.lineage_warning ? 'rgba(239,68,68,0.06)' : 'var(--color-bg-input)',
                    border: `1px solid ${c.lineage_warning ? 'rgba(239,68,68,0.3)' : 'var(--color-border)'}`,
                    borderRadius: '8px', fontSize: '0.82rem',
                  }}>
                    <div>
                      <span>{c.source_label}</span>
                      {c.doc_id && <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginLeft: '8px' }}>ID: {c.doc_id?.slice(0, 8)}...</span>}
                    </div>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      <span className={`badge badge-${c.status?.toLowerCase() || 'active'}`}>{c.status_label}</span>
                      {c.lineage_warning && <span style={{ color: 'var(--color-superseded)', fontSize: '0.7rem', fontWeight: 700 }}>⚠️ SUPERSEDED</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
