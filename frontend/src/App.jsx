import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Chat from './pages/Chat.jsx'
import Sidebar from './components/Sidebar.jsx'
import { fetchCurrentUser } from './api/client.js'

function ProtectedLayout({ user, setUser }) {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar user={user} setUser={setUser} />
      <main style={{ flex: 1, minWidth: 0 }}>
        <Outlet />
      </main>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCurrentUser()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
        booting jarvis...
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route element={user ? <ProtectedLayout user={user} setUser={setUser} /> : <Navigate to="/" replace />}>
        <Route path="/dashboard" element={<Dashboard user={user} />} />
        <Route path="/chat" element={<Chat />} />
      </Route>
    </Routes>
  )
}