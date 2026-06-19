import React, { useState } from 'react';
import ChatPanel from './ChatPanel';
import TracePanel from './TracePanel';

function App() {
  const [sessionId] = useState('session_' + Date.now());
  const [activeTab, setActiveTab] = useState('chat');
  const [traceData, setTraceData] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0d0d0d', color: '#e2e8f0', fontFamily: "'Inter', sans-serif" }}>
      {/* 顶栏 */}
      <div style={{ padding: '0 24px', height: '52px', background: '#111111', borderBottom: '1px solid #222', display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
        <span style={{ fontWeight: '700', color: '#fff', fontSize: '15px', marginRight: '16px', letterSpacing: '0.5px' }}>⚡ AgentOS</span>
        {['chat', 'trace'].map(tab => (
          <button key={tab} onClick={() => !loading && setActiveTab(tab)}
            style={{ padding: '6px 18px', borderRadius: '20px', border: 'none', cursor: loading && tab === 'trace' ? 'not-allowed' : 'pointer',
              background: activeTab === tab ? '#6366f1' : 'transparent',
              color: activeTab === tab ? '#fff' : '#666',
              fontSize: '13px', fontWeight: '500',
              opacity: loading && tab === 'trace' ? 0.3 : 1,
              transition: 'all 0.2s' }}>
            {tab === 'chat' ? '💬 Chat' : '🔍 Trace'}
          </button>
        ))}
        {loading && <span style={{ fontSize: '12px', color: '#6366f1', marginLeft: '8px' }}>● 处理中...</span>}
      </div>

      {/* 内容区 */}
      <div style={{ flex: 1, overflow: 'hidden', display: activeTab === 'chat' ? 'flex' : 'none', flexDirection: 'column' }}>
        <ChatPanel sessionId={sessionId} onTrace={setTraceData} messages={messages} setMessages={setMessages} setLoading={setLoading} />
      </div>
      <div style={{ flex: 1, overflow: 'hidden', display: activeTab === 'trace' ? 'flex' : 'none', flexDirection: 'column' }}>
        <TracePanel data={traceData} />
      </div>
    </div>
  );
}

export default App;