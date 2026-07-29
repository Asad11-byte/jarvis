import { loginWithGoogle } from '../api/client.js'

const CAPABILITIES = [
  { label: 'MAILBOX', detail: 'read + draft replies' },
  { label: 'CALENDAR', detail: 'full read/write' },
  { label: 'TASKS', detail: 'full read/write' },
]

export default function Login() {
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.eyebrow}>JARVIS // TEXT ASSISTANT</div>
        <h1 style={styles.title}>Sign in to bring<br />Jarvis online.</h1>
        <p style={styles.sub}>
          Connects to your Google account to read mail, draft replies, and manage
          your calendar and tasks. It never sends email on its own.
        </p>

        <button style={styles.googleBtn} onClick={loginWithGoogle}>
          <GoogleIcon />
          Continue with Google
        </button>

        <div style={styles.divider} />

        <ul style={styles.capList}>
          {CAPABILITIES.map((c) => (
            <li key={c.label} style={styles.capRow}>
              <span style={styles.capDot} />
              <span style={styles.capLabel}>{c.label}</span>
              <span style={styles.capDetail}>{c.detail}</span>
            </li>
          ))}
        </ul>

        <p style={styles.footnote}>
          Draft-only by design — emails are created in your mailbox for you to review and send yourself.
        </p>
      </div>
    </div>
  )
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">
      <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.9c1.7-1.57 2.7-3.87 2.7-6.62z"/>
      <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.26c-.8.54-1.84.86-3.06.86-2.35 0-4.34-1.59-5.05-3.72H.9v2.33A9 9 0 0 0 9 18z"/>
      <path fill="#FBBC05" d="M3.95 10.7A5.4 5.4 0 0 1 3.66 9c0-.59.1-1.17.29-1.7V4.97H.9A9 9 0 0 0 0 9c0 1.45.35 2.83.9 4.03l3.05-2.33z"/>
      <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.46 3.44 1.35l2.58-2.58C13.46.89 11.43 0 9 0A9 9 0 0 0 .9 4.97l3.05 2.33C4.66 5.17 6.65 3.58 9 3.58z"/>
    </svg>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'grid',
    placeItems: 'center',
    padding: '24px',
  },
  card: {
    width: '100%',
    maxWidth: 440,
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 16,
    padding: '40px 36px',
    boxShadow: '0 0 0 1px rgba(73,224,209,0.04), 0 20px 60px rgba(0,0,0,0.5)',
  },
  eyebrow: {
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
    letterSpacing: '0.14em',
    color: 'var(--accent)',
    marginBottom: 18,
  },
  title: {
    fontFamily: 'var(--font-display)',
    fontWeight: 700,
    fontSize: 30,
    lineHeight: 1.2,
    margin: '0 0 14px',
  },
  sub: {
    color: 'var(--text-muted)',
    fontSize: 14.5,
    lineHeight: 1.6,
    margin: '0 0 28px',
  },
  googleBtn: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    background: '#fff',
    color: '#1f1f1f',
    border: 'none',
    borderRadius: 10,
    padding: '13px 16px',
    fontSize: 14.5,
    fontWeight: 600,
    cursor: 'pointer',
  },
  divider: {
    height: 1,
    background: 'var(--border)',
    margin: '28px 0 20px',
  },
  capList: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  capRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    fontFamily: 'var(--font-mono)',
    fontSize: 12.5,
  },
  capDot: {
    width: 6,
    height: 6,
    borderRadius: '50%',
    background: 'var(--accent)',
    boxShadow: '0 0 8px var(--accent)',
    flexShrink: 0,
  },
  capLabel: {
    color: 'var(--text)',
    letterSpacing: '0.05em',
    minWidth: 76,
  },
  capDetail: {
    color: 'var(--text-muted)',
  },
  footnote: {
    marginTop: 24,
    fontSize: 12,
    color: 'var(--text-muted)',
    lineHeight: 1.5,
  },
}
