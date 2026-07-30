import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../api/client.js'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState(null)
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    setSending(true)

    try {
      const data = await sendChatMessage(text, conversationId)
      setConversationId(data.conversation_id)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }])
    } catch (err) {
      const detail = err?.response?.data?.detail
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: detail || 'Something went wrong reaching Jarvis. Please try again.' },
      ])
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.empty}>Ask Jarvis to check your mail, manage your calendar, or handle tasks.</div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ ...styles.bubbleRow, justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ ...styles.bubble, ...(m.role === 'user' ? styles.bubbleUser : styles.bubbleAssistant) }}>
              {m.content}
            </div>
          </div>
        ))}
        {sending && (
          <div style={styles.bubbleRow}>
            <div style={{ ...styles.bubble, ...styles.bubbleAssistant, ...styles.typing }}>thinking…</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} style={styles.inputRow}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message Jarvis…"
          style={styles.input}
        />
        <button type="submit" style={styles.sendBtn} disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

const styles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '32px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  empty: {
    color: 'var(--text-muted)',
    fontSize: 14,
    margin: 'auto',
  },
  bubbleRow: { display: 'flex' },
  bubble: {
    maxWidth: '65%',
    padding: '10px 14px',
    borderRadius: 12,
    fontSize: 14,
    lineHeight: 1.5,
    whiteSpace: 'pre-wrap',
  },
  bubbleUser: {
    background: 'var(--accent-dim)',
    color: 'var(--text)',
    border: '1px solid rgba(73, 224, 209, 0.25)',
  },
  bubbleAssistant: {
    background: 'var(--surface-raised)',
    color: 'var(--text)',
    border: '1px solid var(--border)',
  },
  typing: {
    color: 'var(--text-muted)',
    fontStyle: 'italic',
  },
  inputRow: {
    display: 'flex',
    gap: 10,
    padding: 20,
    borderTop: '1px solid var(--border)',
  },
  input: {
    flex: 1,
    background: 'var(--surface-raised)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '12px 14px',
    color: 'var(--text)',
    fontSize: 14,
    outline: 'none',
  },
  sendBtn: {
    background: 'var(--accent)',
    color: '#0a0e14',
    border: 'none',
    borderRadius: 10,
    padding: '0 20px',
    fontWeight: 600,
    fontSize: 14,
    cursor: 'pointer',
  },
}