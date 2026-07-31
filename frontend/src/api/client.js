import axios from 'axios'

// Base already includes /api -- every call below is relative to that,
// so /api never needs to be repeated (or forgotten) path by path.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

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

export async function sendChatMessage(message, conversationId) {
  const res = await api.post('/chat', { message, conversation_id: conversationId })
  return res.data
}

export async function fetchEvents() {
  const res = await api.get('/events')
  return res.data
}

export async function fetchTodos() {
  const res = await api.get('/todos')
  return res.data
}

export async function updateTodo(id, updates) {
  const res = await api.patch(`/todos/${id}`, updates)
  return res.data
}

export async function deleteTodo(id) {
  await api.delete(`/todos/${id}`)
}