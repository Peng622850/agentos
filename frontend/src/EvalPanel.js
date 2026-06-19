import React, { useState, useEffect } from 'react';

function EvalPanel() {
  const [badCases, setBadCases] = useState([]);
  const [history, setHistory] = useState([]);
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('bad_cases');

  const fetchData = async () => {
    const [bcRes, histRes] = await Promise.all([
      fetch('http://localhost:8000/api/eval/bad_cases'),
      fetch('http://localhost:8000/api/eval/prompt_history'),
    ]);
    const bc = await bcRes.json();
    const hist = await histRes.json();
    setBadCases(bc.bad_cases || []);
    setHistory(hist.history || []);
    setCurrentPrompt(hist.current_prompt || '');
  };

  useEffect(() => { fetchData(); }, []);

  const triggerFlywheel = async () => {
    setLoading(true);
    await fetch('http://localhost:8000/api/eval/flywheel', { method: 'POST' });
    await fetchData();
    setLoading(false);
  };

  const rollback = async (version) => {
    await fetch('http://localhost:8000/api/eval/rollback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version })
    });
    await fetchData();
  };

  const errorColors = {
    planning_error: '#f87171',
    tool_error: '#fbbf24',
    quality_error: '#c084fc',
    none: '#4ade80',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '20px', gap: '16px', overflowY: 'auto' }}>
      {/* 顶部统计 */}
      <div style={{ display: 'flex', gap: '12px' }}>
        {[
          { label: 'Bad Cases', value: badCases.length, color: '#f87171' },
          { label: 'Prompt版本', value: history.length, color: '#6366f1' },
          { label: '待优化', value: badCases.length >= 10 ? '可触发' : `${badCases.length}/10`, color: '#fbbf24' },
        ].map((s, i) => (
          <div key={i} style={{ flex: 1, padding: '14px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px' }}>
            <div style={{ fontSize: '11px', color: '#555', marginBottom: '4px' }}>{s.label}</div>
            <div style={{ fontSize: '22px', fontWeight: '700', color: s.color }}>{s.value}</div>
          </div>
        ))}
        <button onClick={triggerFlywheel} disabled={loading || badCases.length === 0}
          style={{ padding: '14px 20px', borderRadius: '10px', border: 'none', background: loading ? '#333' : '#6366f1', color: '#fff', cursor: loading || badCases.length === 0 ? 'not-allowed' : 'pointer', fontWeight: '600', fontSize: '13px', opacity: badCases.length === 0 ? 0.4 : 1 }}>
          {loading ? '优化中...' : '⚡ 触发飞轮'}
        </button>
      </div>

      {/* Tab切换 */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {[['bad_cases', 'Bad Cases'], ['prompt_history', 'Prompt历史'], ['current_prompt', '当前Prompt']].map(([key, label]) => (
          <button key={key} onClick={() => setActiveSection(key)}
            style={{ padding: '6px 16px', borderRadius: '20px', border: 'none', cursor: 'pointer',
              background: activeSection === key ? '#6366f1' : '#1a1a1a', color: activeSection === key ? '#fff' : '#555', fontSize: '12px' }}>
            {label}
          </button>
        ))}
      </div>

      {/* Bad Cases */}
      {activeSection === 'bad_cases' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {badCases.length === 0 && <div style={{ color: '#555', fontSize: '13px' }}>暂无bad case，继续使用系统积累数据</div>}
          {badCases.map((c, i) => (
            <div key={i} style={{ padding: '14px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '10px', background: '#2a2a2a', color: errorColors[c.error_type] || '#94a3b8' }}>{c.error_type}</span>
                <span style={{ fontSize: '12px', color: '#f87171' }}>评分 {c.score}/5</span>
              </div>
              <div style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '6px' }}>问题：{c.user_input}</div>
              <div style={{ fontSize: '12px', color: '#555' }}>原因：{c.reason}</div>
            </div>
          ))}
        </div>
      )}

      {/* Prompt历史 */}
      {activeSection === 'prompt_history' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {history.length === 0 && <div style={{ color: '#555', fontSize: '13px' }}>暂无优化历史</div>}
          {history.map((h, i) => (
            <div key={i} style={{ padding: '14px 16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ color: '#6366f1', fontWeight: '600', fontSize: '13px' }}>v{i + 1}</span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', color: '#555' }}>bad cases: {h.stats?.bad_case_count} · 均分: {h.stats?.avg_score?.toFixed(1)}</span>
                  <button onClick={() => rollback(i + 1)}
                    style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid #333', background: 'transparent', color: '#94a3b8', cursor: 'pointer', fontSize: '11px' }}>
                    回滚
                  </button>
                </div>
              </div>
              <div style={{ fontSize: '12px', color: '#555', whiteSpace: 'pre-wrap' }}>{h.prompt?.slice(0, 200)}...</div>
            </div>
          ))}
        </div>
      )}

      {/* 当前Prompt */}
      {activeSection === 'current_prompt' && (
        <div style={{ padding: '16px', background: '#1a1a1a', border: '1px solid #222', borderRadius: '10px' }}>
          <div style={{ fontSize: '12px', color: '#555', marginBottom: '8px' }}>当前生效的Planner Prompt</div>
          <pre style={{ fontSize: '13px', color: '#e2e8f0', whiteSpace: 'pre-wrap', margin: 0 }}>{currentPrompt}</pre>
        </div>
      )}
    </div>
  );
}

export default EvalPanel;