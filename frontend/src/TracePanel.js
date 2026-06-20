import React from 'react';

const nodeColors = {
  planner: '#6366f1',
  action: '#f87171',
  critic: '#4ade80',
};

function TracePanel({ data }) {
  if (!data.length) return (
    <div style={{ padding: '24px', color: '#555', fontSize: '13px' }}>发送一条消息后查看Trace</div>
  );

  // 从SSE数据里提取tracer记录
  const spans = data.map(event => {
    const nodeName = Object.keys(event)[0];
    const nodeData = event[nodeName];
    return { node: nodeName, ...nodeData };
  });

  const totalLatency = spans.reduce((sum, s) => sum + (s.latency_ms || 0), 0);

  return (
    <div style={{ padding: '20px', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        {[
          { label: '节点数', value: spans.length },
          { label: '总耗时', value: totalLatency ? `${totalLatency}ms` : '-' },
        ].map((s, i) => (
          <div key={i} style={{ padding: '12px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px' }}>
            <div style={{ fontSize: '11px', color: '#555', marginBottom: '4px' }}>{s.label}</div>
            <div style={{ fontSize: '18px', fontWeight: '700', color: '#e2e8f0' }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {spans.map((span, i) => {
          const color = nodeColors[span.node] || '#94a3b8';
          return (
            <div key={i} style={{ padding: '14px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px', borderLeft: `3px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ color, fontWeight: '700', fontSize: '13px', textTransform: 'uppercase' }}>{span.node}</span>
                <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#555' }}>
                  {span.latency_ms && <span>⏱ {span.latency_ms}ms</span>}
                  {span.score && <span style={{ color: '#4ade80' }}>★ {span.score}</span>}
                </div>
              </div>
              {span.node === 'planner' && (
                <div style={{ fontSize: '12px', color: '#666' }}>{span.plan?.slice(0, 150)}...</div>
              )}
              {span.node === 'action' && (
                <div style={{ fontSize: '12px', color: '#666' }}>{span.result?.slice(0, 150)}...</div>
              )}
              {span.node === 'critic' && (
                <div style={{ fontSize: '12px', color: '#666' }}>
                  评分：<span style={{ color: '#4ade80' }}>{span.score}/5</span>
                  　类型：<span style={{ color: '#fbbf24' }}>{span.error_type}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TracePanel;