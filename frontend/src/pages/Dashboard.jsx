export default function Dashboard({ user }) {
  return (
    <div style={{ padding: 32 }}>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)', letterSpacing: '0.14em', marginBottom: 16 }}>
        JARVIS // ONLINE
      </div>
      <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 24, marginBottom: 4 }}>
        Welcome, {user.full_name || user.email}
      </h1>
      <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
        Google account connected. Head to Chat to talk to Jarvis, or check your upcoming events and tasks in the sidebar.
      </p>
    </div>
  )
}