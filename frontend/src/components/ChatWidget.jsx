import { useState, useRef, useEffect } from 'react';
import { HiOutlineChat, HiOutlineX, HiOutlinePaperAirplane } from 'react-icons/hi';
import { sendChat } from '../api';

const EXAMPLE_QUESTIONS = [
  'What is total revenue?',
  'Who are the top 5 customers?',
  'Which product category has highest sales?',
  'Show me monthly sales trend',
  'What is the churn risk distribution?',
];

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hi! I\'m your AI analytics assistant. Ask me anything about your RetailMart data — revenue, customers, products, trends, and more!' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (text) => {
    const question = (text || input).trim();
    if (!question || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: question }]);
    setLoading(true);

    try {
      const res = await sendChat(question);
      const msg = {
        role: 'assistant',
        text: res.answer || res.response || 'I could not generate a response.',
        sql: res.sql_query || null,
        sources: res.sources || [],
      };
      setMessages(prev => [...prev, msg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `Sorry, something went wrong: ${err.response?.data?.detail || err.message}`,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <button className="chat-fab" onClick={() => setOpen(!open)} id="chat-fab">
        {open ? <HiOutlineX /> : <HiOutlineChat />}
      </button>

      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-avatar">🤖</div>
              <div>
                <div className="chat-header-title">AI Analytics Agent</div>
                <div className="chat-header-status">● Online — GPT-4o-mini</div>
              </div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)}><HiOutlineX /></button>
          </div>

          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-msg ${msg.role}`}>
                <div>{msg.text}</div>
                {msg.sql && (
                  <div className="msg-sql">{msg.sql}</div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="msg-sources">
                    {msg.sources.map((s, j) => (
                      <span key={j} className="msg-source-tag">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-typing">
                <span /><span /><span />
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {messages.length === 1 && (
            <div style={{ padding: '0 16px 8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {EXAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '16px',
                    padding: '5px 12px',
                    color: 'var(--text-secondary)',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onMouseOver={e => { e.target.style.borderColor = 'var(--accent-blue)'; e.target.style.color = 'var(--accent-blue-light)'; }}
                  onMouseOut={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--text-secondary)'; }}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          <div className="chat-input-area">
            <input
              className="chat-input"
              placeholder="Ask about your data..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              id="chat-input"
            />
            <button className="chat-send" onClick={() => handleSend()} disabled={loading || !input.trim()} id="chat-send">
              <HiOutlinePaperAirplane />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
