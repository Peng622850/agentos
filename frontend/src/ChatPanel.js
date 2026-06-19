import React, { useState, useRef, useEffect } from 'react';

function ChatPanel({ sessionId, onTrace, messages, setMessages, setLoading }) {
  const [input, setInput] = useState('');
  const [loading, setLocalLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLocalLoading(true);
    setLoading(true);

    const resp = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: userMsg })
    });

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let traceEvents = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      const lines = text.split('\n').filter(l => l.startsWith('data:'));
      for (const line of lines) {
        try {
          const data = JSON.parse(line.slice(5));
          traceEvents.push(data);
          if (data.critic) {
            setMessages(prev => [...prev, {
              role: 'assistant',
              content: data.critic.result,
              score: data.critic.score
            }]);
          }
        } catch {}
      }
    }
    onTrace(traceEvents);
    setLocalLoading(false);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 消息区 */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#333', marginTop: '80px', fontSize: '14px' }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚡</div>
            <div style={{ color: '#555' }}>AgentOS 已就绪，输入任何问题开始</div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {m.role === 'assistant' && (
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', marginRight: '8px', flexShrink: 0, marginTop: '2px' }}>⚡</div>
            )}
            <div style={{
              maxWidth: '68%', padding: '12px 16px', borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              background: m.role === 'user' ? '#6366f1' : '#1a1a1a',
              border: m.role === 'assistant' ? '1px solid #222' : 'none',
              color: '#e2e8f0', fontSize: '14px', lineHeight: '1.6', whiteSpace: 'pre-wrap'
            }}>
              {m.content}
              {m.score > 0 && (
                <div style={{ marginTop: '8px', fontSize: '11px', color: '#6366f1', borderTop: '1px solid #222', paddingTop: '6px' }}>
                  质量评分 {m.score}/5 ★
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}>⚡</div>
            <div style={{ padding: '12px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '18px 18px 18px 4px', color: '#555', fontSize: '13px' }}>
              Planner → Action → Critic...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 输入区 */}
      <div style={{ padding: '16px 24px', borderTop: '1px solid #1a1a1a', background: '#0d0d0d' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: '12px', padding: '8px 8px 8px 16px' }}>
          <textarea value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="输入消息，Enter发送，Shift+Enter换行..."
            rows={1}
            style={{ flex: 1, background: 'transparent', border: 'none', color: '#e2e8f0', fontSize: '14px', outline: 'none', resize: 'none', lineHeight: '1.5', maxHeight: '120px', fontFamily: 'inherit' }} />
          <button onClick={send} disabled={loading}
            style={{ padding: '8px 16px', borderRadius: '8px', border: 'none', background: loading ? '#333' : '#6366f1', color: '#fff', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: '600', fontSize: '13px', flexShrink: 0 }}>
            发送
          </button>
        </div>
        <div style={{ textAlign: 'center', marginTop: '8px', fontSize: '11px', color: '#333' }}>AgentOS · Planner · Action · Critic</div>
      </div>
    </div>
  );
}

export default ChatPanel;