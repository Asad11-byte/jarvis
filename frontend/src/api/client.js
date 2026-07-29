import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // sends the signed session cookie set by /auth/callback
})

export function loginWithGoogle() {
  // Full page redirect -- this must NOT be an axios/fetch call,
  // the browser needs to navigate to Google's consent screen.
  window.location.href = `${API_URL}/auth/login`
}

export async function fetchCurrentUser() {
  const res = await api.get('/auth/me')
  return res.data
}

export async function logout() {
  await api.post('/auth/logout')
}
