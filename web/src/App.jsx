import React, { useState, useEffect, useRef, useCallback } from 'react';

const API = 'http://127.0.0.1:8022';

const PALETTE = [
  { type: 'event', label: 'Event BeginPlay', color: '#ff6d5a', icon: '▶' },
  { type: 'function', label: 'Probe Templates', color: '#00bfff', icon: '⚡' },
  { type: 'function', label: 'Template Race', color: '#00bfff', icon: '⚡' },
  { type: 'function', label: 'Replay Fill', color: '#00bfff', icon: '⚡' },
  { type: 'ai', label: 'LLM Node', color: '#a855f7', icon: '🧠' },
  { type: 'save', label: 'Save Blueprint', color: '#22c55e', icon: '💾' },
];

export default function App() {
  const [health, setHealth] = useState(null);
  const [project, setProject] = useState(null);
  const [loadingProject, setLoadingProject] = useState(true);
  
  const [activeTab, setActiveTab] = useState('workflow');
  const [nodes, setNodes] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [toast, setToast] = useState(null);
  const [zoom, setZoom] = useState(1);
  
  const dragRef = useRef(null);
  const canvasRef = useRef(null);
  const fileRef = useRef(null);

  // -- Initialization --
  useEffect(() => {
    fetch(`${API}/api/health`)
      .then(r => r.json())
      .then(data => {
        setHealth(data);
        if (data.active_project) {
          setProject(data.active_project);
        }
        setLoadingProject(false);
      })
      .catch(() => setLoadingProject(false));
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  // -- Project Setup --
  const handleCreateProject = async (e) => {
    e.preventDefault();
    const name = e.target.name.value;
    const context = e.target.context.value;
    try {
      const res = await fetch(`${API}/api/project/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, context })
      });
      const data = await res.json();
      if (data.success) setProject(data.project);
      else alert(data.error);
    } catch (err) { alert("Failed to connect to gateway."); }
  };

  // -- Canvas Drag & Zoom --
  const handleWheel = useCallback((e) => {
    if (e.ctrlKey) {
      e.preventDefault();
      setZoom(z => Math.min(Math.max(0.2, z - e.deltaY * 0.001), 3));
    }
  }, []);

  useEffect(() => {
    const el = canvasRef.current;
    if (el && activeTab === 'workflow') el.addEventListener('wheel', handleWheel, { passive: false });
    return () => { if (el) el.removeEventListener('wheel', handleWheel); };
  }, [activeTab, handleWheel]);

  const onMouseDown = useCallback((e, id) => {
    if (e.button !== 0) return;
    const node = nodes.find(n => n.id === id);
    dragRef.current = { id, startX: e.clientX / zoom - node.x, startY: e.clientY / zoom - node.y };
    setSelectedId(id);
    e.stopPropagation();
  }, [nodes, zoom]);

  useEffect(() => {
    const onMove = (e) => {
      if (!dragRef.current) return;
      const { id, startX, startY } = dragRef.current;
      setNodes(prev => prev.map(n => n.id === id ? { ...n, x: e.clientX / zoom - startX, y: e.clientY / zoom - startY } : n));
    };
    const onUp = () => { dragRef.current = null; };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [zoom]);

  // -- Node Actions --
  const addNode = (item) => {
    setNodes(prev => [...prev, {
      id: `n${Date.now()}`, type: item.type, label: item.label, color: item.color, icon: item.icon,
      x: 300 + Math.random() * 200, y: 200 + Math.random() * 100,
      data: item.type === 'ai' ? { prompt: '' } : {}
    }]);
  };

  const selected = nodes.find(n => n.id === selectedId);
  const updateData = (k, v) => setNodes(p => p.map(n => n.id === selectedId ? { ...n, data: { ...n.data, [k]: v } } : n));

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (ev) => {
      try {
        const content = JSON.parse(ev.target.result);
        showToast("Analyzing notebook via LLM...");
        const res = await fetch(`${API}/api/analyze-notebook`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notebook: content })
        });
        const data = await res.json();
        if (data.nodes) {
          // ensure nodes have visual properties
          const formatted = data.nodes.map(n => ({ ...n, color: '#00bfff', icon: '⚡' }));
          setNodes(formatted);
          showToast("Blueprint Generated!");
        }
      } catch (err) { showToast("Failed analysis."); }
    };
    reader.readAsText(file);
    e.target.value = null;
  };

  const handleSave = async () => {
    const v = prompt("Save Version As (e.g. v21):", "v_new");
    if (!v) return;
    await fetch(`${API}/api/save`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: v, code: `# Nodes: ${nodes.length}` })
    });
    showToast(`Saved as ${v}`);
  };

  // -- Render Setup Modal --
  if (!loadingProject && !project) {
    return (
      <div className="overlay">
        <div className="modal">
          <h2>Create Workspace</h2>
          <p>Initialize a new project environment. The system will create isolated memory, history, and notebooks for this competition.</p>
          <form onSubmit={handleCreateProject}>
            <div className="ins-field">
              <label className="ins-label">Project / Competition Name</label>
              <input name="name" className="ins-input" required placeholder="e.g. AI-Agent-Security" />
            </div>
            <div className="ins-field">
              <label className="ins-label">Competition Context / Rules</label>
              <textarea name="context" className="ins-code" required placeholder="Paste Kaggle rules, evaluation metric..." />
            </div>
            <div className="modal-actions">
              <button type="submit" className="btn btn-primary">Create Workspace</button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="header">
        <div className="header-left">
          <div className="logo">ROS / {project || 'Loading...'}</div>
          <div className="header-tabs">
            <div className={`tab ${activeTab === 'workflow' ? 'active' : ''}`} onClick={() => setActiveTab('workflow')}>Workflow</div>
            <div className={`tab ${activeTab === 'executions' ? 'active' : ''}`} onClick={() => setActiveTab('executions')}>Executions</div>
            <div className={`tab ${activeTab === 'context' ? 'active' : ''}`} onClick={() => setActiveTab('context')}>Context</div>
          </div>
        </div>
        <div className="header-right">
          <div className="status-pill">
            <div className={`dot ${health?.status === 'online' ? 'green' : 'red'}`}></div>
            Gateway {health?.status === 'online' ? 'Online' : 'Offline'}
          </div>
          <div className="status-pill">
            <div className={`dot ${health?.ollama_available ? 'green' : 'amber'}`}></div>
            {health?.ollama_available ? 'Ollama' : 'GLM-4 (Ollama Offline)'}
          </div>
          {activeTab === 'workflow' && (
            <>
              <button className="btn" onClick={() => setZoom(1)}>Reset Zoom</button>
              <button className="btn btn-primary" onClick={handleSave}>Save Blueprint</button>
            </>
          )}
        </div>
      </div>

      <div className="main-area">
        {activeTab === 'workflow' && (
          <>
            <div className="sidebar">
              <div className="sidebar-section">
                <div className="sidebar-title">Actions</div>
                <button className="btn" style={{ width: '100%', marginBottom: '0.5rem' }} onClick={() => fileRef.current.click()}>Upload Notebook</button>
                <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".ipynb" onChange={handleUpload} />
                <button className="btn" style={{ width: '100%' }} onClick={() => {
                   fetch(`${API}/api/create-notebook`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nodes }) })
                     .then(r=>r.json()).then(d=>showToast(d.message));
                }}>Export .ipynb</button>
              </div>
              <div className="sidebar-section">
                <div className="sidebar-title">Nodes</div>
                {PALETTE.map((p, i) => (
                  <div key={i} className="node-item" onClick={() => addNode(p)}>
                    <div className="node-icon" style={{ background: p.color }}>{p.icon}</div>
                    {p.label}
                  </div>
                ))}
              </div>
            </div>

            <div className="canvas" ref={canvasRef} onClick={() => setSelectedId(null)}>
              <div className="canvas-inner" style={{ transform: `scale(${zoom})`, transformOrigin: '0 0' }}>
                <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                  {nodes.map((node, i) => {
                    if (i === 0) return null;
                    const prev = nodes[i - 1];
                    const x1 = prev.x + 260; const y1 = prev.y + 40;
                    const x2 = node.x; const y2 = node.y + 40;
                    const cx = (x1 + x2) / 2;
                    return <path key={i} d={`M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`} stroke="#666" strokeWidth="2" fill="none" />;
                  })}
                </svg>

                {nodes.map(node => (
                  <div key={node.id} className={`n8n-node ${selectedId === node.id ? 'selected' : ''}`}
                    style={{ left: node.x, top: node.y }}
                    onMouseDown={(e) => onMouseDown(e, node.id)}
                    onClick={(e) => { e.stopPropagation(); setSelectedId(node.id); }}
                  >
                    <div className="node-header">
                      <div className="icon" style={{ background: node.color || '#00bfff' }}>{node.icon || '⚡'}</div>
                      <div>
                        <div className="title">{node.label}</div>
                        <div className="type">{node.type}</div>
                      </div>
                    </div>
                    <div className="node-body">
                      <div className="pin-row">
                        <div className="pin"><div className="pin-circle filled"></div> In</div>
                        <div className="pin">Out <div className="pin-circle filled"></div></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {selected && (
              <div className="inspector-panel">
                <div className="ins-header">
                  <div className="ins-title">Node Inspector</div>
                  <button className="ins-close" onClick={() => setSelectedId(null)}>×</button>
                </div>
                <div className="ins-body">
                  <div className="ins-field">
                    <label className="ins-label">Label</label>
                    <input className="ins-input" value={selected.label} onChange={e => setNodes(p => p.map(n => n.id === selected.id ? { ...n, label: e.target.value } : n))} />
                  </div>
                  {selected.data && Object.entries(selected.data).map(([k, v]) => (
                    <div className="ins-field" key={k}>
                      <label className="ins-label">{k}</label>
                      {k === 'prompt' ? 
                        <textarea className="ins-code" value={v} onChange={e => updateData(k, e.target.value)} /> :
                        <input className="ins-input" value={typeof v === 'object' ? JSON.stringify(v) : v} onChange={e => updateData(k, e.target.value)} />
                      }
                    </div>
                  ))}
                  <button className="btn" style={{ width: '100%', marginTop: '1rem', borderColor: '#ef4444', color: '#ef4444' }} onClick={() => {
                    setNodes(p => p.filter(n => n.id !== selected.id));
                    setSelectedId(null);
                  }}>Delete Node</button>
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === 'executions' && (
          <div className="tab-content">
            <div className="card">
              <h3>Execution History</h3>
              <p style={{ color: 'var(--text-muted)' }}>Graph and roadmap execution logs will appear here based on project history.</p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => window.open(`${API}/api/graph`)}>Raw JSON Graph</button>
            </div>
          </div>
        )}

        {activeTab === 'context' && (
          <div className="tab-content">
            <div className="card">
              <h3>Project Context</h3>
              <p style={{ color: 'var(--text-muted)' }}>Workspace: <strong>{project}</strong></p>
              <p style={{ marginTop: '1rem' }}>Active hypotheses and memory loop insights will be populated as the AI learns over 30 days.</p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={async () => {
                 const res = await fetch(`${API}/api/writeup`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ context: "Full context" }) });
                 const data = await res.json();
                 alert("Generated Writeup:\n" + data.writeup);
              }}>Generate Kaggle Writeup</button>
            </div>
          </div>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
    </>
  );
}
