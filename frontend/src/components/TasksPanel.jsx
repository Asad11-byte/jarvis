import { useEffect, useState } from 'react'
import { fetchTodos, updateTodo, deleteTodo } from '../api/client.js'

export default function TasksPanel() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    load()
  }, [])

  function load() {
    setLoading(true)
    fetchTodos()
      .then(setTasks)
      .catch(() => setError('Could not load tasks'))
      .finally(() => setLoading(false))
  }

  async function toggleComplete(task) {
    setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, completed: !t.completed } : t)))
    try {
      await updateTodo(task.id, { completed: !task.completed })
    } catch {
      load() // resync on failure
    }
  }

  async function remove(task) {
    setTasks((prev) => prev.filter((t) => t.id !== task.id))
    try {
      await deleteTodo(task.id)
    } catch {
      load()
    }
  }

  if (loading) return <div style={styles.muted}>loading…</div>
  if (error) return <div style={styles.errorText}>{error}</div>
  if (tasks.length === 0) return <div style={styles.muted}>No tasks</div>

  return (
    <ul style={styles.list}>
      {tasks.slice(0, 8).map((t) => (
        <li key={t.id} style={styles.item}>
          <label style={styles.taskRow}>
            <input type="checkbox" checked={t.completed} onChange={() => toggleComplete(t)} />
            <span style={{ ...styles.itemTitle, ...(t.completed ? styles.completed : {}) }}>{t.title}</span>
          </label>
          <button onClick={() => remove(t)} style={styles.deleteBtn} aria-label="Delete task">
            ×
          </button>
        </li>
      ))}
    </ul>
  )
}

const styles = {
  list: { listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 6 },
  item: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '6px 8px',
    background: 'var(--surface-raised)',
    border: '1px solid var(--border)',
    borderRadius: 8,
  },
  taskRow: { display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', flex: 1, minWidth: 0 },
  itemTitle: { fontSize: 12.5, color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  completed: { color: 'var(--text-muted)', textDecoration: 'line-through' },
  deleteBtn: {
    background: 'transparent',
    border: 'none',
    color: 'var(--text-muted)',
    fontSize: 16,
    lineHeight: 1,
    cursor: 'pointer',
    padding: '0 4px',
  },
  muted: { fontSize: 12, color: 'var(--text-muted)', padding: '4px 2px' },
  errorText: { fontSize: 12, color: 'var(--danger)', padding: '4px 2px' },
}