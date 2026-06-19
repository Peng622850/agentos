import React from 'react';

const nodeColors = {
  planner: '#7C9EF8',
  action: '#f87171',
  critic: '#4ade80',
};

function TracePanel({ data }) {
  if (!data.length) return (
    <div style={{ padding: '24px', color: '#64748b' }}>发送一条消息后查看Trace</div>
  );

  return (
    <div style={{ padding: '16px', overflowY: 'auto', height: '100%' }}>
      <div style={{ marginBottom: '16px', color: '#94a3b8', fontSize: '13px' }}>Run Trace — {data.length} 个节点</div>
      {data.map((event, i) => {
        const nodeName = Object.keys(event)[0];
        const nodeData = event[nodeName];
        const color = nodeColors[nodeName] || '#94a3b8';
        return (
          <div key={i} style={{ marginBottom: '12px', padding: '12px 16px', background: '#1a1d2e', borderRadius: '8px', borderLeft: `3px solid ${color}` }}>
            <div style={{ color, fontWeight: 'bold', fontSize: '13px', marginBottom: '6px', textTransform: 'uppercase' }}>{nodeName}</div>
            {nodeName === 'planner' && <div style={{ color: '#94a3b8', fontSize: '12px' }}>{nodeData.plan?.slice(0, 200)}...</div>}
            {nodeName === 'action' && <div style={{ color: '#94a3b8', fontSize: '12px' }}>{nodeData.result?.slice(0, 200)}...</div>}
            {nodeName === 'critic' && (
              <div style={{ color: '#94a3b8', fontSize: '12px' }}>
                评分: <span style={{ color: '#4ade80' }}>{nodeData.score}/5</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default TracePanel;