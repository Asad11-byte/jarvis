import { logout } from '../api/client.js'
import { useNavigate } from 'react-router-dom'

export default function Dashboard({ user, setUser }) {
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    setUser(null)
    navigate('/')
  }

  return (
    <div style={{ padding: 32, fontFamily: 'var(--font-body)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)', letterSpacing: '0.14em' }}>
          JARVIS // ONLINE
        </div>
        <button
          onClick={handleLogout}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            borderRadius: 8,
            padding: '8px 14px',
            cursor: 'pointer',
            fontSize: 13,
          }}
        >
          Sign out
        </button>
      </div>

      <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 24, marginBottom: 4 }}>
        Welcome, {user.full_name || user.email}
      </h1>
      <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
        Google account connected. Chat, mailbox, calendar, and tasks land here in the next build phase.
      </p>
    </div>
  )
}
