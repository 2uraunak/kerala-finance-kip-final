import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'

export default function GSTAssistant() {
  const { authHeaders } = useAuthStore()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Namaste! I am the GST Policy Assistant for the Kerala Finance Department. Ask me anything about GST rates, circulars, notifications, or compliance requirements.',
      citations: [],
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [rateQuery, setRateQuery] = useState('')
  const [rateResult, setRateResult] = useState(null)

  const EXAMPLE_QUERIES = [
    'What is the GST rate for works contract services to government?',
    'Explain GST exemption for pure services to government',
    'Latest GST circular on construction services',
    'HSN code for software development services',
  ]

  const sendMessage = async (msg = input) => {
    if (!msg.trim() || loading) return
    const userMsg = { role: 'user', content: msg }
    setMessages(m => [...m, userMsg])
    setInput('')
    setLoading(true)

    try {
      const resp = await fetch('/api/v1/gst/query', {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: msg }),
      })
      if (resp.ok) {
        const data = await resp.json()
        setMessages(m => [...m, {
          role: 'assistant',
          content: data.answer,
          citations: data.citations || [],
          gstRate: data.gst_rate_info,
          confidence: data.confidence,
        }])
      }
    } catch (e) {}
    setLoading(false)
  }

  const lookupRate = async () => {
    if (!rateQuery) return
    try {
      const resp = await fetch(`/api/v1/gst/rate-lookup?description=${encodeURIComponent(rateQuery)}`, { headers: authHeaders() })
      if (resp.ok) setRateResult(await resp.json())
    } catch (e) {}
  }

  return (
    <div>
      <div className="page-header">
        <h1>💹 GST Policy Assistant</h1>
        <p>AI-powered GST rate lookup, circular analysis, and compliance guidance</p>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* Chat */}
        <div className="chat-container" style={{ height: 'calc(100vh - 260px)' }}>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                  background: msg.role === 'user' ? 'var(--gradient-accent)' : 'rgba(96,165,250,0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.9rem',
                }}>
                  {msg.role === 'user' ? '👤' : '💹'}
                </div>
                <div style={{ flex: 1 }}>
                  <div className={`message-bubble ${msg.role}`}>
                    <p style={{ color: msg.role === 'user' ? '#1a0f00' : 'var(--color-text-primary)', margin: 0 }}>
                      {msg.content}
                    </p>
                  </div>
                  {msg.gstRate && (
                    <div style={{
                      marginTop: '8px',
                      background: 'rgba(34,197,94,0.1)',
                      border: '1px solid rgba(34,197,94,0.3)',
                      borderRadius: '8px', padding: '8px 12px', fontSize: '0.78rem',
                    }}>
                      <strong style={{ color: 'var(--color-active)' }}>GST Rate: {msg.gstRate.rate}</strong>
                      {' '} • HSN: {msg.gstRate.hsn} • Notification: {msg.gstRate.notification}
                    </div>
                  )}
                  {msg.citations?.length > 0 && (
                    <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {msg.citations.map((c, ci) => (
                        <span key={ci} className="source-label" style={{ fontSize: '0.7rem' }}>
                          {c.source_label}
                          <span className={`badge badge-${c.status_label?.toLowerCase()}`} style={{ fontSize: '0.6rem' }}>{c.status_label}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(96,165,250,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>💹</div>
                <div className="message-bubble assistant">
                  <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                    {[0, 1, 2].map(i => (
                      <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent)', animation: 'pulse 1s infinite', animationDelay: `${i * 0.2}s` }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="chat-input-area">
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
              {EXAMPLE_QUERIES.map(q => (
                <button key={q} style={{
                  background: 'var(--color-bg-input)', border: '1px solid var(--color-border)',
                  borderRadius: '999px', padding: '3px 10px', fontSize: '0.68rem',
                  color: 'var(--color-text-muted)', cursor: 'pointer',
                }}
                  onClick={() => sendMessage(q)}
                >{q.slice(0, 35)}...</button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input className="input" value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about GST rates, circulars, exemptions..." />
              <button className="btn btn-primary" onClick={() => sendMessage()} disabled={loading || !input.trim()}>
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Rate Lookup Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card">
            <h4 style={{ marginBottom: '12px' }}>⚡ Quick Rate Lookup</h4>
            <div className="input-group">
              <label className="input-label">Describe goods/service</label>
              <input className="input" value={rateQuery} onChange={e => setRateQuery(e.target.value)}
                placeholder="e.g. works contract, software, food..." />
            </div>
            <button className="btn btn-secondary btn-sm" onClick={lookupRate}>Lookup Rate</button>
            {rateResult && (
              <div style={{
                marginTop: '12px',
                background: rateResult.found ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)',
                border: `1px solid ${rateResult.found ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
                borderRadius: '8px', padding: '12px', fontSize: '0.82rem',
              }}>
                {rateResult.found ? (
                  <>
                    <div style={{ color: 'var(--color-active)', fontWeight: 700, marginBottom: '4px' }}>
                      GST Rate: {rateResult.rate}
                    </div>
                    <div>HSN Code: {rateResult.hsn}</div>
                    <div>Notification: {rateResult.notification}</div>
                  </>
                ) : (
                  <div style={{ color: 'var(--color-text-muted)' }}>{rateResult.message}</div>
                )}
              </div>
            )}
          </div>

          <div className="card">
            <h4 style={{ marginBottom: '8px', fontSize: '0.9rem' }}>📋 Common GST Rates</h4>
            {[
              { item: 'Works Contract (Roads/Railways)', rate: '12%', hsn: '9954' },
              { item: 'Works Contract (Others)', rate: '18%', hsn: '9954' },
              { item: 'Pure Services to Government', rate: 'Nil', hsn: '9997' },
              { item: 'Software/IT Services', rate: '18%', hsn: '9983' },
              { item: 'Consultancy Services', rate: '18%', hsn: '9983' },
            ].map(r => (
              <div key={r.item} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--color-border)', fontSize: '0.8rem' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>{r.item}</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 700 }}>{r.rate}</span>
                  <span style={{ color: 'var(--color-text-muted)' }}>HSN:{r.hsn}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
