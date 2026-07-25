import React, { useEffect, useState } from 'react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [graph, setGraph] = useState(null);
  const [roadmap, setRoadmap] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeTab, setActiveTab] = useState('canvas');
  const [activeProvider, setActiveProvider] = useState('Ollama Local');

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
        console.error("Gateway offline:", err);
      }
    }
    fetchData();
  }, []);

  const nodes = graph?.nodes || [
    { id: 'v16', label: 'v16 Baseline', type: 'version', status: 'success', score: '87.660', strategy: 'Replay Throughput', evidence: 'VERIFIED' },
    { id: 'v20', label: 'v20 Engine', type: 'version', status: 'pending', score: 'Pending', strategy: 'Controlled Live Diversity', evidence: 'HYPOTHESIS' },
    { id: 'strat_relay', label: 'Template Racing', type: 'strategy', status: 'active', gain: '+80', evidence: 'STRONG_EVIDENCE' },
    { id: 'strat_cap', label: '8910s Latency Cap', type: 'strategy', status: 'active', gain: 'Prevents Timeout', evidence: 'VERIFIED' },
    { id: 'strat_dedup', label: 'Semantic Dedup', type: 'strategy', status: 'testing', gain: '+1.8', evidence: 'HYPOTHESIS' }
  ];

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div>
          <h1 className="logo">RESEARCH OPERATING SYSTEM</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.2rem' }}>
            Array-Level Visual Analysis & Decision Intelligence Platform (n8n Workspace)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div className="status-badge">
            <div className="status-dot"></div>
            <span>{health?.status === 'online' ? 'GATEWAY: 127.0.0.1:8022' : 'GATEWAY: STANDBY'}</span>
          </div>
          <button className="btn" onClick={() => window.location.reload()}>Sync Gateway</button>
        </div>
      </header>

      {/* Provider & Execution Bar */}
      <div style={{ background: 'var(--bg-secondary)', padding: '1rem 1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-secondary)' }}>ACTIVE MODEL PROVIDER:</span>
          <select 
            value={activeProvider} 
            onChange={(e) => setActiveProvider(e.target.value)}
            style={{ background: 'var(--bg-primary)', color: 'var(--accent-cyan)', border: '1px solid var(--border-color)', padding: '0.5rem 1rem', borderRadius: '8px', fontWeight: '600', cursor: 'pointer' }}
          >
            <option value="Ollama Local">Ollama Local (http://127.0.0.1:11434)</option>
            <option value="GLM-4 Cloud (ZhipuAI)">GLM-4 Cloud / GLM-4-Flash (API Key Active)</option>
          </select>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: '600' }}>
          Key Status: Configured in local_only/gateway_env.txt (Un-tracked)
        </div>
      </div>

      {/* Interactive n8n-Style Workflow Canvas */}
      <div className="n8n-canvas">
        <div className="canvas-title">
          <span>INTERACTIVE ARRAY-LEVEL DIGITAL DIAGRAM (N8N WORKFLOW STYLE)</span>
          <span>CLICK ANY NODE TO INSPECT STRATEGY & CAUSAL EVIDENCE</span>
        </div>

        <div className="node-flow-grid">
          {nodes.map((node, index) => (
            <React.Fragment key={node.id}>
              <div 
                className={`n8n-node ${selectedNode?.id === node.id ? 'selected' : ''}`}
                onClick={() => setSelectedNode(node)}
              >
                <div className="node-header">
                  <div className="node-icon">{node.type === 'version' ? 'V' : 'S'}</div>
                  <div>
                    <div className="node-title">{node.label}</div>
                    <div className="node-type">{node.type.toUpperCase()} NODE</div>
                  </div>
                </div>

                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                  {node.score ? `Score: ${node.score}` : `Impact: ${node.gain}`}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className={`badge ${node.evidence === 'VERIFIED' ? 'badge-verified' : 'badge-hypothesis'}`}>
                    {node.evidence || 'HYPOTHESIS'}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>Inspect →</span>
                </div>
              </div>

              {index < nodes.length - 1 && <div className="connector-line"></div>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Inspector Panel for Selected Node */}
      {selectedNode && (
        <div className="inspector-drawer">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ color: 'var(--accent-cyan)', fontSize: '1.2rem' }}>
              Node Strategy Analysis: {selectedNode.label}
            </h3>
            <button 
              onClick={() => setSelectedNode(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem' }}
            >
              ✕ Close Inspector
            </button>
          </div>

          <div className="grid-2">
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>EVIDENCE & CAUSAL REASONING</p>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
                <div>Node ID: {selectedNode.id}</div>
                <div>Evidence Tag: <span className="badge badge-verified">{selectedNode.evidence || 'HYPOTHESIS'}</span></div>
                <div>Status: {selectedNode.status}</div>
                <div style={{ marginTop: '0.5rem', color: 'var(--accent-cyan)' }}>
                  Causal Chain: {selectedNode.id} → [MEASURED_LATENCY] → [PREVENTS_TIMEOUT] → HIGH_SCORE
                </div>
              </div>
            </div>

            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>RECOMMENDED ACTION</p>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                <p>Preserve this node in the current baseline architecture. Avoid modifying latency caps or introducing unverified static padding.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Decision Intelligence & Roadmap Grid */}
      <div className="grid-2" style={{ marginTop: '2rem' }}>
        <div className="card">
          <div className="card-title">Decision Intelligence Priorities</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {roadmap.map(item => (
              <div key={item.priority} style={{ padding: '0.8rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '700', marginBottom: '0.3rem' }}>
                  <span style={{ color: 'var(--accent-cyan)' }}>P{item.priority}: {item.experiment}</span>
                  <span style={{ color: 'var(--accent-green)', fontFamily: 'var(--font-mono)' }}>{item.expected_gain}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>{item.reason}</p>
                <span className="badge badge-verified">{item.evidence_level}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Local Gateway CLI Execution Commands</div>
          <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1rem', borderRadius: '8px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', lineHeight: '1.6' }}>
            <div style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}># Start Gateway Local Server:</div>
            <div style={{ color: 'var(--accent-cyan)' }}>python -m uvicorn gateway.server:app --port 8022</div>
            <div style={{ color: 'var(--text-secondary)', margin: '0.8rem 0 0.5rem 0' }}># Run Terminal Analysis Dashboard:</div>
            <div style={{ color: 'var(--accent-cyan)' }}>python -m ros.cli.dashboard</div>
            <div style={{ color: 'var(--text-secondary)', margin: '0.8rem 0 0.5rem 0' }}># Run Repository Self-Test Protocol:</div>
            <div style={{ color: 'var(--accent-cyan)' }}>python -m ros.cli.selftest</div>
          </div>
        </div>
      </div>
    </div>
  );
}
