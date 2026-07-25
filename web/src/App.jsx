import React, { useState, useEffect, useRef, useCallback } from 'react';

const API = 'http://127.0.0.1:8022';

const PALETTE_ITEMS = [
  { type: 'event', label: 'Event BeginPlay', icon: 'E', color: '#991b1b' },
  { type: 'function', label: 'Probe Templates', icon: 'F', color: '#1d4ed8' },
  { type: 'function', label: 'Template Race', icon: 'F', color: '#1d4ed8' },
  { type: 'function', label: 'Replay Fill', icon: 'F', color: '#1d4ed8' },
  { type: 'variable', label: 'Latency Cap 8910s', icon: 'V', color: '#15803d' },
  { type: 'variable', label: 'Semantic Dedup', icon: 'V', color: '#15803d' },
  { type: 'ai', label: 'Ollama Generate', icon: 'AI', color: '#7c3aed' },
  { type: 'ai', label: 'GLM-4 Cloud', icon: 'AI', color: '#7c3aed' },
  { type: 'save', label: 'Save To Disk', icon: 'S', color: '#d97706' },
];

const DEFAULT_NODES = [
  { id: 'n1', type: 'event', label: 'Event BeginPlay', x: 60, y: 80,
    pins: { out: [{ name: 'Exec', kind: 'exec' }] } },
  { id: 'n2', type: 'function', label: 'Probe Templates', x: 420, y: 60,
    pins: { in: [{ name: 'Exec', kind: 'exec' }, { name: 'Templates', kind: 'string' }],
            out: [{ name: 'Exec', kind: 'exec' }, { name: 'Results', kind: 'object' }] },
    data: { templates: '5', reps: '5' } },
  { id: 'n3', type: 'function', label: 'Template Race', x: 800, y: 60,
    pins: { in: [{ name: 'Exec', kind: 'exec' }, { name: 'Probes', kind: 'object' }],
            out: [{ name: 'Exec', kind: 'exec' }, { name: 'Winner', kind: 'string' }] },
    data: { metric: 'effective_cost = median_latency / fire_rate' } },
  { id: 'n4', type: 'function', label: 'Replay Fill', x: 1180, y: 60,
    pins: { in: [{ name: 'Exec', kind: 'exec' }, { name: 'Template', kind: 'string' }, { name: 'Budget', kind: 'float' }],
            out: [{ name: 'Exec', kind: 'exec' }, { name: 'Candidates', kind: 'object' }] },
    data: { budget: '8910', method: 'measured_latency_cumulative' } },
  { id: 'n5', type: 'ai', label: 'Ollama Generate', x: 420, y: 360,
    pins: { in: [{ name: 'Exec', kind: 'exec' }, { name: 'Prompt', kind: 'string' }],
            out: [{ name: 'Exec', kind: 'exec' }, { name: 'Response', kind: 'string' }] },
    data: { prompt: '', provider: 'auto' } },
  { id: 'n6', type: 'save', label: 'Save To Disk', x: 800, y: 360,
    pins: { in: [{ name: 'Exec', kind: 'exec' }, { name: 'Version', kind: 'string' }, { name: 'Code', kind: 'string' }] },
    data: { version: 'v21' } },
];

export default function App() {
  const [nodes, setNodes] = useState(DEFAULT_NODES);
  const [selectedId, setSelectedId] = useState(null);
  const [health, setHealth] = useState(null);
  const [toast, setToast] = useState(null);
  const [aiResponse, setAiResponse] = useState('');
  const [generating, setGenerating] = useState(false);
  const dragRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/health`).then(r => r.json()).then(setHealth).catch(() => {});
  }, []);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Dragging ──
  const onMouseDown = useCallback((e, nodeId) => {
    if (e.button !== 0) return;
    const node = nodes.find(n => n.id === nodeId);
    dragRef.current = { id: nodeId, startX: e.clientX - node.x, startY: e.clientY - node.y };
    setSelectedId(nodeId);
    e.stopPropagation();
  }, [nodes]);

  useEffect(() => {
    const onMove = (e) => {
      if (!dragRef.current) return;
      const { id, startX, startY } = dragRef.current;
      setNodes(prev => prev.map(n => n.id === id ? { ...n, x: e.clientX - startX, y: e.clientY - startY } : n));
    };
    const onUp = () => { dragRef.current = null; };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, []);

  // ── Add node from palette ──
  const addNode = (item) => {
    const id = `n${Date.now()}`;
    setNodes(prev => [...prev, {
      id, type: item.type, label: item.label,
      x: 200 + Math.random() * 400, y: 150 + Math.random() * 200,
      pins: {
        in: item.type !== 'event' ? [{ name: 'Exec', kind: 'exec' }] : undefined,
        out: [{ name: 'Exec', kind: 'exec' }],
      },
      data: item.type === 'ai' ? { prompt: '', provider: 'auto' } : {},
    }]);
  };

  // ── Delete selected ──
  const deleteSelected = () => {
    if (!selectedId) return;
    setNodes(prev => prev.filter(n => n.id !== selectedId));
    setSelectedId(null);
  };

  // ── Selected node ──
  const selected = nodes.find(n => n.id === selectedId);

  // ── Update node data ──
  const updateNodeData = (key, val) => {
    setNodes(prev => prev.map(n => n.id === selectedId ? { ...n, data: { ...n.data, [key]: val } } : n));
  };

  // ── Generate via Ollama/GLM ──
  const runGenerate = async () => {
    if (!selected?.data?.prompt) return;
    setGenerating(true);
    setAiResponse('');
    try {
      const res = await fetch(`${API}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: selected.data.prompt, provider: selected.data.provider || 'auto' }),
      });
      const data = await res.json();
      setAiResponse(data.response || '');
      showToast(`Generated via ${data.provider}`);
    } catch (err) {
      setAiResponse(`Error: ${err.message}`);
      showToast('Generation failed', 'error');
    } finally {
      setGenerating(false);
    }
  };

  // ── Save to disk ──
  const saveToDisk = async () => {
    const ver = selected?.data?.version || 'v_new';
    const blueprint = { nodes: nodes.map(n => ({ id: n.id, type: n.type, label: n.label, x: n.x, y: n.y, data: n.data })) };
    try {
      const res = await fetch(`${API}/api/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: ver,
          manifest: `# Auto-saved from ROS Blueprint Editor\nversion: ${ver}\nnodes: ${nodes.length}\narchitecture_fingerprint:\n${nodes.map(n => `  - ${n.label}`).join('\n')}\n`,
          code: `# Blueprint: ${ver}\n# Nodes: ${nodes.map(n => n.label).join(' -> ')}\n# Generated by ROS Blueprint Editor\n`,
        }),
      });
      const data = await res.json();
      showToast(`Saved ${data.files?.length || 0} files to ${ver}/`);
    } catch (err) {
      showToast('Save failed', 'error');
    }
  };

  // ── Pin color helper ──
  const pinColor = (kind) => {
    const map = { exec: '#fff', float: '#00cc66', string: '#ff00ff', object: '#0099ff', bool: '#cc0000' };
    return map[kind] || '#888';
  };

  return (
    <>
      {/* ─── Top Bar ─── */}
      <div className="topbar">
        <div className="topbar-left">
          <span className="topbar-logo">ROS BLUEPRINT EDITOR</span>
          <div className="topbar-status">
            <div className="topbar-dot" style={{ background: health?.status === 'online' ? '#22c55e' : '#ef4444' }}></div>
            <span>{health?.status === 'online' ? 'Gateway Online' : 'Gateway Offline'}</span>
          </div>
          <div className="topbar-status" style={{ color: health?.ollama_available ? '#22c55e' : '#f59e0b' }}>
            <div className="topbar-dot" style={{ background: health?.ollama_available ? '#22c55e' : '#f59e0b', boxShadow: `0 0 8px ${health?.ollama_available ? '#22c55e' : '#f59e0b'}` }}></div>
            <span>{health?.ollama_available ? 'Ollama Connected' : 'Ollama Offline (GLM Fallback)'}</span>
          </div>
        </div>
        <div className="topbar-right">
          <button className="btn-sm" onClick={deleteSelected}>Delete Node</button>
          <button className="btn-sm btn-primary" onClick={saveToDisk}>Save Blueprint</button>
        </div>
      </div>

      <div className="editor-layout">
        {/* ─── Left Palette ─── */}
        <div className="palette">
          <div className="palette-title">Blueprint Nodes</div>
          {PALETTE_ITEMS.map((item, i) => (
            <div key={i} className="palette-item" onClick={() => addNode(item)}>
              <div className="palette-icon" style={{ background: item.color }}>{item.icon}</div>
              <span>{item.label}</span>
            </div>
          ))}

          <div className="palette-title" style={{ marginTop: '1.5rem' }}>Quick Actions</div>
          <div className="palette-item" onClick={() => window.open(`${API}/api/graph`, '_blank')}>
            <div className="palette-icon" style={{ background: '#334155' }}>G</div>
            <span>View Graph JSON</span>
          </div>
          <div className="palette-item" onClick={() => window.open(`${API}/api/roadmap`, '_blank')}>
            <div className="palette-icon" style={{ background: '#334155' }}>R</div>
            <span>View Roadmap</span>
          </div>
        </div>

        {/* ─── Blueprint Canvas ─── */}
        <div className="canvas" ref={canvasRef} onClick={() => setSelectedId(null)}>
          <div className="canvas-inner">
            {/* Wire connections (simple line rendering) */}
            <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
              {nodes.map((node, i) => {
                if (i === 0) return null;
                const prev = nodes[i - 1];
                if (!prev) return null;
                const x1 = prev.x + 280;
                const y1 = prev.y + 30;
                const x2 = node.x;
                const y2 = node.y + 30;
                const cx = (x1 + x2) / 2;
                return (
                  <path key={`wire-${i}`}
                    d={`M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`}
                    stroke="rgba(255,255,255,0.15)"
                    strokeWidth="2"
                    fill="none"
                    strokeDasharray={node.type === 'ai' ? '6 3' : 'none'}
                  />
                );
              })}
            </svg>

            {/* Blueprint Nodes */}
            {nodes.map(node => (
              <div key={node.id}
                className={`bp-node ${selectedId === node.id ? 'selected' : ''}`}
                style={{ left: node.x, top: node.y }}
                onMouseDown={(e) => onMouseDown(e, node.id)}
                onClick={(e) => { e.stopPropagation(); setSelectedId(node.id); }}
              >
                <div className={`bp-node-header ${node.type}`}>
                  <span>{node.label}</span>
                </div>
                <div className="bp-node-body">
                  {/* Input Pins */}
                  {node.pins?.in?.map((pin, i) => (
                    <div key={`in-${i}`} className="bp-pin-row">
                      <div className="bp-pin">
                        {pin.kind === 'exec'
                          ? <div className="bp-pin-exec-arrow"></div>
                          : <div className="bp-pin-dot" style={{ borderColor: pinColor(pin.kind) }}></div>
                        }
                        <span>{pin.name}</span>
                      </div>
                    </div>
                  ))}
                  {/* Output Pins */}
                  {node.pins?.out?.map((pin, i) => (
                    <div key={`out-${i}`} className="bp-pin-row" style={{ justifyContent: 'flex-end' }}>
                      <div className="bp-pin" style={{ flexDirection: 'row-reverse' }}>
                        {pin.kind === 'exec'
                          ? <div className="bp-pin-exec-arrow"></div>
                          : <div className="bp-pin-dot" style={{ borderColor: pinColor(pin.kind), background: pinColor(pin.kind) + '33' }}></div>
                        }
                        <span>{pin.name}</span>
                      </div>
                    </div>
                  ))}

                  {/* Node-specific inline data */}
                  {node.data?.metric && (
                    <div style={{ marginTop: '0.4rem', fontSize: '0.7rem', color: 'var(--accent)', fontFamily: 'var(--mono)' }}>
                      {node.data.metric}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ─── Right Inspector ─── */}
        <div className="inspector">
          {selected ? (
            <>
              <div className="inspector-title">Node Inspector: {selected.label}</div>

              <div className="inspector-field">
                <div className="inspector-label">NODE TYPE</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                  <span className={`badge-sm ${selected.type === 'event' ? 'badge-red' : selected.type === 'ai' ? 'badge-amber' : 'badge-green'}`}>
                    {selected.type.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="inspector-field">
                <div className="inspector-label">LABEL</div>
                <input className="inspector-input" value={selected.label}
                  onChange={e => setNodes(prev => prev.map(n => n.id === selected.id ? { ...n, label: e.target.value } : n))} />
              </div>

              <div className="inspector-field">
                <div className="inspector-label">POSITION (X, Y)</div>
                <div style={{ fontSize: '0.8rem', fontFamily: 'var(--mono)', color: 'var(--text-dim)' }}>
                  {Math.round(selected.x)}, {Math.round(selected.y)}
                </div>
              </div>

              {/* Data fields */}
              {selected.data && Object.entries(selected.data).map(([key, val]) => (
                <div className="inspector-field" key={key}>
                  <div className="inspector-label">{key.toUpperCase()}</div>
                  {key === 'prompt' ? (
                    <textarea className="inspector-code" value={val}
                      placeholder="Enter prompt for Ollama / GLM-4..."
                      onChange={e => updateNodeData(key, e.target.value)} />
                  ) : (
                    <input className="inspector-input" value={val}
                      onChange={e => updateNodeData(key, e.target.value)} />
                  )}
                </div>
              ))}

              {/* AI Generate Button */}
              {selected.type === 'ai' && (
                <div className="inspector-field">
                  <button className="btn-sm btn-primary" style={{ width: '100%', padding: '0.6rem' }}
                    onClick={runGenerate} disabled={generating}>
                    {generating ? 'Generating...' : 'Run Ollama / GLM-4 Generation'}
                  </button>
                  {aiResponse && (
                    <div style={{ marginTop: '0.6rem', background: '#0a0e1a', border: '1px solid #1e293b', borderRadius: '6px', padding: '0.6rem' }}>
                      <div className="inspector-label">AI RESPONSE</div>
                      <pre style={{ fontSize: '0.75rem', color: 'var(--accent)', fontFamily: 'var(--mono)', whiteSpace: 'pre-wrap', maxHeight: '200px', overflow: 'auto' }}>
                        {aiResponse}
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Save Button */}
              {selected.type === 'save' && (
                <div className="inspector-field">
                  <button className="btn-sm btn-primary" style={{ width: '100%', padding: '0.6rem' }} onClick={saveToDisk}>
                    Save Blueprint to Disk
                  </button>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="inspector-title">Blueprint Overview</div>
              <div className="inspector-field">
                <div className="inspector-label">TOTAL NODES</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{nodes.length}</div>
              </div>
              <div className="inspector-field">
                <div className="inspector-label">GATEWAY</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--green)', fontWeight: 600 }}>
                  {health?.status === 'online' ? `Online (${health.workspace?.split('\\').pop()})` : 'Offline'}
                </div>
              </div>
              <div className="inspector-field">
                <div className="inspector-label">OLLAMA STATUS</div>
                <div style={{ fontSize: '0.85rem', color: health?.ollama_available ? 'var(--green)' : 'var(--amber)', fontWeight: 600 }}>
                  {health?.ollama_available ? 'Connected (127.0.0.1:11434)' : 'Offline - Using GLM-4 Cloud Fallback'}
                </div>
              </div>
              <div className="inspector-field">
                <div className="inspector-label">HOW TO USE</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', lineHeight: 1.6 }}>
                  Click palette items to add nodes. Drag nodes to position them.
                  Click a node to inspect and edit its properties.
                  Use AI nodes to generate prompts via Ollama or GLM-4 Cloud.
                  Use Save nodes to persist your blueprint to disk.
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Toast notifications */}
      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
    </>
  );
}
