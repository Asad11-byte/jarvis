import { useEffect, useState } from 'react'
import { fetchEvents } from '../api/client.js'

export default function EventsPanel() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchEvents()
      .then(setEvents)
      .catch(() => setError('Could not load events'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={styles.muted}>loading…</div>
  if (error) return <div style={styles.errorText}>{error}</div>
  if (events.length === 0) return <div style={styles.muted}>No upcoming events</div>

  return (
    <ul style={styles.list}>
      {events.slice(0, 6).map((e) => (
        <li key={e.id} style={styles.item}>
          <div style={styles.itemTitle}>{e.summary}</div>
          <div style={styles.itemMeta}>{formatDate(e.start)}</div>
        </li>
      ))}
    </ul>
  )
}

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  if (isNaN(d)) return dt
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

const styles = {
  list: { listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 },
  item: {
    padding: '8px 10px',
    background: 'var(--surface-raised)',
    border: '1px solid var(--border)',
    borderRadius: 8,
  },
  itemTitle: { fontSize: 12.5, color: 'var(--text)', fontWeight: 500, marginBottom: 2 },
  itemMeta: { fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' },
  muted: { fontSize: 12, color: 'var(--text-muted)', padding: '4px 2px' },
  errorText: { fontSize: 12, color: 'var(--danger)', padding: '4px 2px' },
}