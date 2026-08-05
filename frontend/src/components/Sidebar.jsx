import { NavLink, useNavigate } from 'react-router-dom'
import { logout } from '../api/client.js'
import EventsPanel from './EventsPanel.jsx'
import TasksPanel from './TasksPanel.jsx'

export default function Sidebar({ user, setUser }) {
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    setUser(null)
    navigate('/')
  }

  const linkStyle = ({ isActive }) => ({
    ...styles.navLink,
    ...(isActive ? styles.navLinkActive : {}),
  })

  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>JARVIS</div>

      <nav style={styles.nav}>
        <NavLink to="/dashboard" style={linkStyle}>Dashboard</NavLink>
        <NavLink to="/chat" style={linkStyle}>Chat</NavLink>
        <NavLink to="/voice" style={linkStyle}>Voice Assistant</NavLink>
      </nav>

      <div style={styles.scrollArea}>
        <div style={styles.section}>
          <div style={styles.sectionTitle}>UPCOMING EVENTS</div>
          <EventsPanel />
        </div>

        <div style={styles.section}>
          <div style={styles.sectionTitle}>TASKS</div>
          <TasksPanel />
        </div>
      </div>

      <div style={styles.footer}>
        <div style={styles.userRow}>
          {user.avatar_url ? (
            <img src={user.avatar_url} alt="" style={styles.avatar} />
          ) : (
            <div style={styles.avatarFallback}>
              {(user.full_name || user.email || '?')[0].toUpperCase()}
            </div>
          )}
          <div style={styles.userText}>
            <div style={styles.userName}>
              {user.full_name || user.email}
            </div>
          </div>
        </div>

        <button onClick={handleLogout} style={styles.logoutBtn}>
          Sign out
        </button>
      </div>
    </aside>
  )
}

const styles = {
  sidebar: {
    width: 280,
    flexShrink: 0,
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--surface)',
    borderRight: '1px solid var(--border)',
    height: '100vh',
    position: 'sticky',
    top: 0,
  },
  brand: {
    padding: '20px 20px 12px',
    fontFamily: 'var(--font-display)',
    fontWeight: 700,
    fontSize: 16,
    letterSpacing: '0.08em',
    color: 'var(--accent)',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
    padding: '0 12px',
    marginBottom: 8,
  },
  navLink: {
    padding: '9px 12px',
    borderRadius: 8,
    fontSize: 13.5,
    color: 'var(--text-muted)',
    textDecoration: 'none',
    fontWeight: 500,
  },
  navLinkActive: {
    color: 'var(--text)',
    background: 'var(--accent-dim)',
  },
  scrollArea: {
    flex: 1,
    overflowY: 'auto',
    padding: '8px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
  },
  section: {},
  sectionTitle: {
    fontFamily: 'var(--font-mono)',
    fontSize: 10.5,
    letterSpacing: '0.1em',
    color: 'var(--text-muted)',
    marginBottom: 8,
  },
  footer: {
    padding: 16,
    borderTop: '1px solid var(--border)',
  },
  userRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: '50%',
  },
  avatarFallback: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    background: 'var(--accent-dim)',
    color: 'var(--accent)',
    display: 'grid',
    placeItems: 'center',
    fontSize: 13,
    fontWeight: 600,
    flexShrink: 0,
  },
  userText: {
    minWidth: 0,
  },
  userName: {
    fontSize: 13,
    color: 'var(--text)',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  logoutBtn: {
    width: '100%',
    background: 'transparent',
    border: '1px solid var(--border)',
    color: 'var(--text-muted)',
    borderRadius: 8,
    padding: '8px 12px',
    cursor: 'pointer',
    fontSize: 12.5,
  },
}