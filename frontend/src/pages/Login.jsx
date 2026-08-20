import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const DEMO_USERS = [
  { username: 'admin_kerala', password: 'Admin@123', role: 'admin', label: '🔴 Admin', desc: 'Full access — all documents & audit' },
  { username: 'analyst_finance', password: 'Analyst@123', role: 'analyst', label: '🟡 Analyst', desc: 'Search, extract, draft policy notes' },
  { username: 'viewer_gst', password: 'Viewer@123', role: 'viewer', label: '⚪ Viewer', desc: 'Read-only — search & view' },
]

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading, error } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    const ok = await login(username, password)
    if (ok) navigate('/')
  }

  const quickLogin = async (user) => {
    const ok = await login(user.username, user.password)
    if (ok) navigate('/')
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--gradient-hero)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background decorative elements */}
      <div style={{
        position: 'absolute', top: '-20%', right: '-10%',
        width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(201,162,39,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
      }} />
      <div style={{
        position: 'absolute', bottom: '-20%', left: '-10%',
        width: 500, height: 500,
        background: 'radial-gradient(circle, rgba(201,162,39,0.05) 0%, transparent 70%)',
        borderRadius: '50%',
      }} />

      <div style={{ width: '100%', maxWidth: 960, zIndex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '48px', alignItems: 'center' }}>
        {/* Left — Branding */}
        <div>
          <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🏛️</div>
          <h1 style={{
            fontSize: '2.5rem', fontWeight: 800,
            background: 'var(--gradient-accent)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginBottom: '8px',
          }}>
            Kerala Finance KIP
          </h1>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 400, color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
            Knowledge Intelligence Platform
          </h2>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', lineHeight: 1.7, marginBottom: '32px' }}>
            Finance Department, Government of Kerala<br />
            Enterprise document intelligence platform for Government Orders,
            Circulars, GST Policy, and Budget documents.
          </p>

          {/* Features list */}
          {[
            '🔍 Hybrid semantic + keyword search',
            '🤖 AI-powered policy note drafting',
            '🔗 Document lineage & version tracking',
            '⚗️ Clause & financial figure extraction',
            '💹 GST policy research assistant',
            '🔒 100% local — data never leaves premises',
          ].map(f => (
            <div key={f} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent)', flexShrink: 0 }} />
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>{f}</span>
            </div>
          ))}
        </div>

        {/* Right — Login Form */}
        <div style={{
          background: 'rgba(17, 24, 39, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--color-border)',
          borderRadius: '24px',
          padding: '40px',
        }}>
          <h3 style={{ marginBottom: '24px', fontSize: '1.25rem' }}>Sign In to KIP</h3>

          {/* Quick Demo Login */}
          <div style={{ marginBottom: '24px' }}>
            <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Quick Demo Access
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {DEMO_USERS.map(u => (
                <button
                  key={u.username}
                  className="btn btn-secondary"
                  style={{ justifyContent: 'flex-start', gap: '12px', padding: '10px 16px' }}
                  onClick={() => quickLogin(u)}
                  disabled={isLoading}
                >
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{u.label}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', flex: 1, textAlign: 'left' }}>{u.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="divider" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>or sign in manually</span>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
          </div>

          {/* Manual Login */}
          <form onSubmit={handleLogin} style={{ marginTop: '20px' }}>
            <div className="input-group">
              <label className="input-label">Username</label>
              <input
                className="input"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="e.g. analyst_finance"
                autoComplete="username"
              />
            </div>
            <div className="input-group">
              <label className="input-label">Password</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>
            {error && (
              <div style={{
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: '8px', padding: '10px 14px',
                color: '#ef4444', fontSize: '0.83rem', marginBottom: '16px',
              }}>
                ❌ {error}
              </div>
            )}
            <button className="btn btn-primary w-full" type="submit" disabled={isLoading}
              style={{ justifyContent: 'center', marginTop: '8px' }}>
              {isLoading ? <><span className="loading-spinner" style={{ width: 16, height: 16 }} /> Signing in...</> : '🔑 Sign In'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
