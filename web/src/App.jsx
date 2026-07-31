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
  
  const [activeTab, setActiveTab] = useState('workflow'); // workflow, chat, executions, context
  const [nodes, setNodes] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [toast, setToast] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [addMenuPos, setAddMenuPos] = useState({ x: 0, y: 0 });
  const [searchFilter, setSearchFilter] = useState('');
  
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatting, setChatting] = useState(false);
  const chatEndRef = useRef(null);
  
  // Execution state
  const [executions, setExecutions] = useState([]);
  const [executionsLoading, setExecutionsLoading] = useState(false);
  const [executionFilter, setExecutionFilter] = useState('all');
  
  const dragRef = useRef(null);
  const canvasRef = useRef(null);
  const fileRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/api/health`)
      .then(r => r.json())
      .then(data => {
        setHealth(data);
        if (data.active_project) setProject(data.active_project);
        setLoadingProject(false);
      })
      .catch(() => setLoadingProject(false));
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    const name = e.target.name.value;
    const context = e.target.context.value;
    // We ignore the actual file upload for the demo frontend since there's no multipart backend setup yet,
    // but the backend creates the /data/ folder for it.
    try {
      const res = await fetch(`${API}/api/project/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, context })
      });
      const data = await res.json();
      if (data.success) {
        setProject(data.project);
        showToast("Project created with data folder.");
      } else {
        alert(data.error);
      }
    } catch (err) { alert("Failed to connect to gateway."); }
  };

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

  const openAddMenu = (x, y) => {
    setAddMenuPos({ x, y });
    setSearchFilter('');
    setShowAddMenu(true);
  };

  const addNode = (item) => {
    setNodes(prev => [...prev, {
      id: `n${Date.now()}`, type: item.type, label: item.label, color: item.color, icon: item.icon,
      x: addMenuPos.x, y: addMenuPos.y,
      data: item.type === 'ai' ? { prompt: '' } : {}
    }]);
    setShowAddMenu(false);
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
          const formatted = data.nodes.map(n => ({ ...n, color: '#00bfff', icon: '⚡' }));
          setNodes(formatted);
          showToast("Blueprint Generated!");
        }
      } catch (err) { showToast("Failed analysis."); }
    };
    reader.readAsText(file);
    e.target.value = null;
    setShowAddMenu(false);
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

  // Chat handling
  useEffect(() => {
    if (activeTab === 'chat' && project) {
      fetch(`${API}/api/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fetch_only: true })
      }).then(r => r.json()).then(d => {
        if (d.history) setChatHistory(d.history);
      });
    }
  }, [activeTab, project]);

  useEffect(() => {
    if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // Execution handlers
  const loadExecutions = async () => {
    setExecutionsLoading(true);
    try {
      const res = await fetch(`${API}/api/executions`);
      const data = await res.json();
      if (data.executions) {
        setExecutions(data.executions);
      }
    } catch (err) {
      console.error('Failed to load executions:', err);
      showToast("Failed to load execution history");
    } finally {
      setExecutionsLoading(false);
    }
  };

  const handleRefreshExecutions = () => {
    loadExecutions();
    showToast("Refreshing execution history...");
  };

  const handleClearExecutions = async () => {
    if (window.confirm("Are you sure you want to clear all execution history?")) {
      try {
        await fetch(`${API}/api/executions/clear`, { method: 'POST' });
        setExecutions([]);
        showToast("Execution history cleared");
      } catch (err) {
        console.error('Failed to clear executions:', err);
        showToast("Failed to clear execution history");
      }
    }
  };

  const viewExecutionDetails = (id) => {
    const execution = executions.find(e => e.id === id);
    if (execution) {
      // In a real app, this might open a modal or sidebar with detailed info
      alert(`Execution Details:\nName: ${execution.name}\nStatus: ${execution.status}\nStart Time: ${new execution.startTime}\nDuration: ${execution.duration}ms\n\nLogs:\n${execution.logs || 'No logs available'}`);
    }
  };

  const rerunExecution = async (id) => {
    const execution = executions.find(e => e.id === id);
    if (execution) {
      showToast(`Re-executing: ${execution.name || 'Unnamed'}`);
      try {
        const res = await fetch(`${API}/api/executions/${id}/rerun`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast("Execution restarted successfully");
          // Refresh executions list to show updated status
          setTimeout(loadExecutions, 2000);
        } else {
          throw new Error(data.error || 'Failed to restart execution');
        }
      } catch (err) {
        console.error('Failed to rerun execution:', err);
        showToast("Failed to restart execution");
      }
    }
  };

  // Load executions on component mount and when project changes
  useEffect(() => {
    if (project) {
      loadExecutions();
      // Set up polling for real-time updates (optional)
      const interval = setInterval(loadExecutions, 10000); // Poll every 10 seconds
      return () => clearInterval(interval);
    }
  }, [project]);

  const sendChatMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg }]);
    setChatting(true);
    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      if (data.history) setChatHistory(data.history);
    } catch (err) {
      showToast("Chat failed");
    } finally {
      setChatting(false);
    }
  };

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
              <textarea name="context" className="ins-code" required placeholder="Paste Kaggle rules, evaluation metric..." style={{ minHeight: '80px' }} />
            </div>
            <div className="ins-field">
              <label className="ins-label">Dataset / Zip File (Optional)</label>
              <input type="file" name="dataset" className="ins-input" style={{ padding: '0.4rem' }} accept=".zip,.csv,.json" />
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
                Files will be stored locally in projects/[name]/data/
              </div>
            </div>
            <div className="modal-actions">
              <button type="submit" className="btn btn-primary">Create Workspace</button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  const filteredPalette = PALETTE.filter(p => p.label.toLowerCase().includes(searchFilter.toLowerCase()));

  return (
    <>
      <div className="header">
        <div className="header-left">
          <div className="logo">ROS</div>
          <div className="header-tabs">
            <div className={`tab ${activeTab === 'workflow' ? 'active' : ''}`} onClick={() => setActiveTab('workflow')}>Workflow</div>
            <div className={`tab ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>Chat</div>
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
            {health?.ollama_available ? 'Ollama Live' : 'GLM-4 Fallback'}
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
            <div className="canvas" ref={canvasRef} onClick={() => {
                setSelectedId(null);
                setShowAddMenu(false);
            }} onContextMenu={(e) => {
                e.preventDefault();
                openAddMenu(e.clientX / zoom, e.clientY / zoom);
            }}>
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
                    onClick={(e) => { e.stopPropagation(); setSelectedId(node.id); setShowAddMenu(false); }}
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
                      <div className="add-branch-btn" onClick={(e) => {
                         e.stopPropagation();
                         openAddMenu(node.x + 320, node.y);
                      }}>+</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button className="fab-add" onClick={(e) => {
                e.stopPropagation();
                openAddMenu(300, 300);
            }}>+</button>

            {showAddMenu && (
              <div className="add-node-panel" style={{ left: Math.min(addMenuPos.x * zoom, window.innerWidth - 320), top: Math.min(addMenuPos.y * zoom, window.innerHeight - 400) }} onClick={e => e.stopPropagation()}>
                <div className="add-node-search">
                  <input autoFocus placeholder="Search nodes..." value={searchFilter} onChange={e => setSearchFilter(e.target.value)} />
                </div>
                <div className="add-node-list">
                  {filteredPalette.map((p, i) => (
                    <div key={i} className="add-node-item" onClick={() => addNode(p)}>
                      <div className="node-icon" style={{ background: p.color }}>{p.icon}</div>
                      {p.label}
                    </div>
                  ))}
                  <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.5rem 0' }} />
                  <div className="add-node-item" onClick={() => fileRef.current.click()}>
                    <div className="node-icon" style={{ background: '#333' }}>📁</div>
                    Upload .ipynb
                  </div>
                </div>
              </div>
            )}
            <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".ipynb" onChange={handleUpload} />

            {selected && (
              <div className="inspector-panel">
                <div className="ins-header">
                  <div className="ins-title">Node Parameters</div>
                  <button className="ins-close" onClick={() => setSelectedId(null)}>×</button>
                </div>
                <div className="ins-body">
                  <div className="ins-field">
                    <label className="ins-label">Node Name</label>
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
        
        {activeTab === 'chat' && (
          <div className="chat-container">
            <div className="chat-history">
              {chatHistory.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '2rem' }}>
                  No messages yet. Ask the AI to explain the notebook or project!
                </div>
              )}
              {chatHistory.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role}`}>
                  <div className={`chat-avatar ${msg.role}`}>{msg.role === 'user' ? 'U' : 'AI'}</div>
                  <div className="chat-msg">
                    <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>{msg.content}</pre>
                  </div>
                </div>
              ))}
              {chatting && (
                <div className="chat-bubble ai">
                  <div className="chat-avatar ai">AI</div>
                  <div className="chat-msg">Thinking...</div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <div className="chat-input-area">
              <form className="chat-input-wrapper" onSubmit={sendChatMessage}>
                <input 
                  placeholder="Ask about the notebook, or generate code..." 
                  value={chatInput} onChange={e => setChatInput(e.target.value)} 
                  disabled={chatting} autoFocus
                />
                <button type="submit" disabled={chatting || !chatInput.trim()}>↑</button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="tab-content">
            <div className="card">
              <h3>Execution History</h3>
              <div className="executions-toolbar">
                <button className="btn btn-sm" onClick={handleRefreshExecutions}>
                  <span className="icon">🔄</span> Refresh
                </button>
                <button className="btn btn-sm" onClick={handleClearExecutions}>
                  <span className="icon">🗑️</span> Clear
                </button>
                <select className="select" value={executionFilter} onChange={e => setExecutionFilter(e.target.value)}>
                  <option value="all">All Executions</option>
                  <option value="successful">Successful</option>
                  <option value="failed">Failed</option>
                  <option value="running">Running</option>
                </select>
              </div>
              {executionsLoading ? (
                <div className="loader">Loading execution history...</div>
              ) : executions.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                  No executions recorded yet. Run workflows to see execution history here.
                </p>
              ) : (
                <div className="executions-list">
                  {executions.map(execution => (
                    <div key={execution.id} className="execution-item">
                      <div className="execution-header">
                        <div className="execution-info">
                          <h4>{execution.name || 'Unnamed Execution'}</h4>
                          <p className="execution-meta">
                            <span className={`status-dot ${execution.status}`}></span>
                            {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
                            <span className="execution-time">{new Date(execution.timestamp).toLocaleTimeString()}</span>
                          </p>
                        </div>
                        <div className="execution-actions">
                          <button className="btn btn-sm" onClick={() => viewExecutionDetails(execution.id)}>
                            <span className="icon">👁️</span> View
                          </button>
                          <button className="btn btn-sm" onClick={() => rerunExecution(execution.id)}>
                            <span className="icon">🔄</span> Rerun
                          </button>
                        </div>
                      </div>
                      {(execution.error || execution.logs) && (
                        <div className="execution-details">
                          {execution.error && (
                            <div className="execution-error">
                              <strong>Error:</strong> {execution.error}
                            </div>
                          )}
                          {execution.logs && (
                            <div className="execution-logs">
                              <strong>Logs:</strong>
                              <pre className="log-pre">{execution.logs}</pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'context' && (
          <div className="tab-content">
            <div className="card">
              <h3>Project Context</h3>
              {contextLoading ? (
                <div className="loader">Loading context...</div>
              ) : !context ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                  No active project. Create or select a project to view context.
                </p>
              ) : (
                <>
                  <div className="context-info">
                    <div className="info-row">
                      <span className="info-label">Project Name:</span>
                      <span className="info-value">{context.name}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Created:</span>
                      <span className="info-value">{context.createdAt ? new Date(context.createdAt).toLocaleString() : 'Unknown'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Last Active:</span>
                      <span className="info-value">{context.updatedAt ? new Date(context.updatedAt).toLocaleString() : 'Unknown'}</span>
                    </div>
                    <div className="info-row">
                      <span className="info-label">Description:</span>
                      <span className="info-value">{context.description || 'No description provided'}</span>
                    </div>
                  </div>
                  
                  <div className="context-section">
                    <h4>Environment Variables</span>
                    <div className="env-vars">
                      {environmentVars.length > 0 ? (
                        environmentVars.map((env, index) => (
                          <div key={index} className="env-var">
                            <span className="env-name">{env.key}</span>
                            <span className="env-value">{env.value}</span>
                          </div>
                        ))
                      ) : (
                        <p style={{ color: 'var(--text-muted)' }}>No environment variables configured.</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="context-section">
                    <h4>Recent Activity</span>
                    <div className="activity-timeline">
                      {recentActivity.length > 0 ? (
                        recentActivity.map((activity, index) => (
                          <div key={index} className="activity-item">
                            <div className="activity-icon">
                              <span className={`activity-type-${activity.type}`}>{activity.icon}</span>
                            </div>
                            <div className="activity-content">
                              <h5>{activity.title}</h5>
                              <p>{activity.description}</p>
                              <span className="activity-time">{new Date(activity.timestamp).toLocaleTimeString()}</span>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p style={{ color: 'var(--text-muted)' }}>No recent activity.</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="context-actions">
                    <button className="btn btn-outline" onClick={handleRefreshContext}>
                      <span className="icon">🔄</span> Refresh Context
                    </button>
                    <button className="btn btn-primary" onClick={handleExportContext}>
                      <span className="icon">📥</span> Export Configuration
                    </button>
                    <button className="btn btn-primary" onClick={() => {
                       const res = await fetch(`${API}/api/writeup`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ context: "Full context" }) });
                       const data = await res.json();
                       alert("Generated Writeup:\n" + data.writeup);
                    }}>
                      <span className="icon">📝</span> Generate Kaggle Writeup
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
    </>
  );
}
