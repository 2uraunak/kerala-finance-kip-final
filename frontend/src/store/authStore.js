import { create } from 'zustand'

const API = '/api/v1'

export const useAuthStore = create((set, get) => ({
  token: localStorage.getItem('kip_token') || null,
  user: JSON.parse(localStorage.getItem('kip_user') || 'null'),
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      const resp = await fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!resp.ok) {
        const err = await resp.json()
        throw new Error(err.detail || 'Login failed')
      }
      const data = await resp.json()
      localStorage.setItem('kip_token', data.access_token)
      localStorage.setItem('kip_user', JSON.stringify(data.user))
      set({ token: data.access_token, user: data.user, isLoading: false })
      return true
    } catch (e) {
      set({ error: e.message, isLoading: false })
      return false
    }
  },

  logout: () => {
    localStorage.removeItem('kip_token')
    localStorage.removeItem('kip_user')
    set({ token: null, user: null })
  },

  authHeaders: () => {
    const token = get().token
    return token ? { Authorization: `Bearer ${token}` } : {}
  },
}))
