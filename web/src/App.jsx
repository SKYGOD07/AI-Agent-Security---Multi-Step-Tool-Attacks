import React, { useEffect, useState } from 'react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [graph, setGraph] = useState(null);
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [healthRes, graphRes, roadmapRes] = await Promise.all([
          fetch('http://127.0.0.1:8022/api/health').then(r => r.json()),
          fetch('http://127.0.0.1:8022/api/graph').then(r => r.json()),
          fetch('http://127.0.0.1:8022/api/roadmap').then(r => r.json())
        ]);
        setHealth(healthRes);
        setGraph(graphRes);
        setRoadmap(roadmapRes.roadmap || []);
      } catch (err) {
        console.error("Gateway connection error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1 className="logo">RESEARCH OPERATING SYSTEM</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            Active AI Security Research & Decision Intelligence Platform
          </p>
        </div>
        <div className="status-badge">
          <div className="status-dot"></div>
          <span>{health?.status === 'online' ? 'LOCAL GATEWAY ONLINE' : 'GATEWAY OFFLINE'}</span>
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <div className="card-title">Research Health Index</div>
          <div className="stat-value">84<span style={{ fontSize: '1.2rem', color: 'var(--accent-cyan)' }}>%</span></div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Verified Knowledge: 61% | Hypotheses: 38
          </p>
        </div>

        <div className="card">
          <div className="card-title">Active Baseline</div>
          <div style={{ fontSize: '1.4rem', fontWeight: '700', color: 'var(--accent-cyan)', marginBottom: '0.5rem' }}>
            v20 (Compact Replay)
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Score: Pending | Latency Cap: 8910s
          </p>
        </div>

        <div className="card">
          <div className="card-title">LLM Router Provider</div>
          <div style={{ fontSize: '1.4rem', fontWeight: '700', color: health?.ollama_available ? 'var(--accent-green)' : 'var(--accent-amber)', marginBottom: '0.5rem' }}>
            {health?.ollama_available ? 'Ollama Local' : 'Standby / Fallback'}
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            URL: http://127.0.0.1:11434
          </p>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="card">
          <div className="card-title">Version Graph Architecture (Array Standard)</div>
          <div className="graph-container">
            {graph?.nodes?.map(node => (
              <div key={node.id} className="node-item">
                <div>
                  <div className="node-label">{node.label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Status: {node.status}
                  </div>
                </div>
                <span className={`badge-tag ${node.status === 'success' ? 'tag-verified' : 'tag-hypothesis'}`}>
                  {node.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Decision Intelligence Roadmap</div>
          <div className="priority-list">
            {roadmap.map(item => (
              <div key={item.priority} className="priority-item">
                <div className="priority-header">
                  <span className="priority-title">P{item.priority}: {item.experiment}</span>
                  <span className="priority-gain">{item.expected_gain}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                  {item.reason}
                </p>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <span className={`badge-tag ${item.evidence_level === 'STRONG_EVIDENCE' ? 'tag-verified' : 'tag-hypothesis'}`}>
                    {item.evidence_level}
                  </span>
                  <span className="badge-tag" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-primary)' }}>
                    CONFIDENCE: {item.confidence}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
