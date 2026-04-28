// Kinetic — Visual Workflow Builder
// Drag-and-drop canvas for composing crypto workflows

const STEP_CATALOG = [
  { type: 'banxa.onramp',          label: 'Onramp',         provider: 'banxa',    defaultParams: { fiat_amount: 1000, fiat_currency: 'GBP', crypto_currency: 'USDC' } },
  { type: 'banxa.offramp',         label: 'Offramp',        provider: 'banxa',    defaultParams: { crypto_amount: 100, fiat_currency: 'GBP' } },
  { type: 'coinbase.buy',          label: 'Buy asset',      provider: 'coinbase', defaultParams: { asset: 'BTC', amount: 100, currency: 'USD' } },
  { type: 'coinbase.sell',         label: 'Sell asset',     provider: 'coinbase', defaultParams: { asset: 'BTC', amount: 100, currency: 'USD' } },
  { type: 'coinbase.withdraw',     label: 'Withdraw',       provider: 'coinbase', defaultParams: { asset: 'BTC', destination: '0x...' } },
  { type: 'privy.create_wallet',   label: 'Create wallet',  provider: 'privy',    defaultParams: { chain: 'ethereum' } },
  { type: 'privy.deposit',         label: 'Deposit',        provider: 'privy',    defaultParams: { asset: 'USDC', destination: '0x...' } },
  { type: 'engine.ai_interpret',   label: 'AI interpret',   provider: 'ai',       defaultParams: { model: 'gpt-4o' } },
  { type: 'engine.condition',      label: 'Condition',      provider: 'engine',   defaultParams: { expression: 'amount > 100' } },
  { type: 'engine.delay',          label: 'Delay',          provider: 'engine',   defaultParams: { seconds: 30 } },
];

const PROVIDER_META = {
  banxa:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  label: 'Banxa' },
  coinbase:{ color: '#3b82f6', bg: 'rgba(59,130,246,0.12)',  label: 'Coinbase' },
  privy:   { color: '#a855f7', bg: 'rgba(168,85,247,0.12)',  label: 'Privy' },
  ai:      { color: '#5b5ff5', bg: 'rgba(91,95,245,0.15)',   label: 'AI Engine' },
  engine:  { color: '#9399a8', bg: 'rgba(147,153,168,0.12)', label: 'Engine' },
};

const PROVIDERS_ORDER = ['banxa','coinbase','privy','ai','engine'];

let nodeIdCounter = 1;
let edgeIdCounter = 1;

function makeNode(type, x, y) {
  const catalog = STEP_CATALOG.find(s => s.type === type);
  return {
    id: `node_${nodeIdCounter++}`,
    type,
    label: catalog?.label ?? type,
    provider: catalog?.provider ?? 'engine',
    x, y,
    params: { ...(catalog?.defaultParams ?? {}) },
  };
}

function makeEdge(from, to) {
  return {
    id: `edge_${edgeIdCounter++}`,
    from,
    to,
    trigger: {
      mode: 'always',
      expression: '',
    },
  };
}

function buildDefaultDemoWorkflow() {
  const nodes = [
    makeNode('privy.create_wallet', 70, 70),
    makeNode('banxa.onramp', 290, 70),
    makeNode('coinbase.buy', 510, 70),
    makeNode('engine.condition', 730, 70),
    makeNode('coinbase.withdraw', 950, 70),
    makeNode('engine.delay', 730, 210),
    makeNode('privy.deposit', 950, 210),
    makeNode('coinbase.sell', 510, 210),
    makeNode('banxa.offramp', 290, 210),
    makeNode('engine.ai_interpret', 70, 210),
  ];

  // Add a realistic expression to the condition step for demo clarity.
  const conditionNode = nodes.find(n => n.type === 'engine.condition');
  if (conditionNode) {
    conditionNode.params = {
      ...conditionNode.params,
      expression: 'portfolio_usd >= 5000',
    };
  }

  const byType = type => nodes.find(n => n.type === type);
  const alwaysEdge = (fromType, toType) => makeEdge(byType(fromType).id, byType(toType).id);
  const conditionalEdge = (fromType, toType, expression) => ({
    ...makeEdge(byType(fromType).id, byType(toType).id),
    trigger: { mode: 'conditional', expression },
  });

  const edges = [
    alwaysEdge('privy.create_wallet', 'banxa.onramp'),
    alwaysEdge('banxa.onramp', 'coinbase.buy'),
    alwaysEdge('coinbase.buy', 'engine.condition'),
    conditionalEdge('engine.condition', 'coinbase.withdraw', 'risk_score < 0.4'),
    conditionalEdge('engine.condition', 'engine.delay', 'risk_score >= 0.4'),
    alwaysEdge('engine.delay', 'privy.deposit'),
    conditionalEdge('coinbase.buy', 'coinbase.sell', 'take_profit_pct >= 8'),
    alwaysEdge('coinbase.sell', 'banxa.offramp'),
    conditionalEdge('banxa.offramp', 'engine.ai_interpret', 'compliance_check = true'),
  ];

  return {
    workflowName: 'demo_treasury_orchestration',
    nodes,
    edges,
  };
}

// ── Port dot ──────────────────────────────────────────
function Port({ kind, nodeId, onPortMouseDown, onPortMouseUp, active }) {
  const size = 10;
  const style = {
    width: size, height: size, borderRadius: '50%',
    background: active ? KColors.primaryLight : KColors.border,
    border: `2px solid ${active ? KColors.primary : KColors.borderStrong}`,
    cursor: kind === 'output' ? 'crosshair' : 'default',
    flexShrink: 0, transition: 'background 120ms, border-color 120ms',
    zIndex: 10, position: 'relative',
  };
  return (
    <div
      style={style}
      onMouseDown={e => { if (kind === 'output') { e.stopPropagation(); onPortMouseDown && onPortMouseDown(nodeId, e); }}}
      onMouseUp={e => { if (kind === 'input') { e.stopPropagation(); onPortMouseUp && onPortMouseUp(nodeId, e); }}}
    />
  );
}

// ── Canvas Node ───────────────────────────────────────
function CanvasNode({ node, selected, onMouseDown, onPortMouseDown, onPortMouseUp, onNodeMouseUp, connectingFrom }) {
  const pm = PROVIDER_META[node.provider] || PROVIDER_META.engine;
  return (
    <div
      onMouseDown={e => onMouseDown(node.id, e)}
      onMouseUp={e => {
        if (connectingFrom && connectingFrom !== node.id) {
          e.stopPropagation();
          onNodeMouseUp && onNodeMouseUp(node.id);
        }
      }}
      style={{
        position: 'absolute', left: node.x, top: node.y,
        width: 180, userSelect: 'none', cursor: 'grab',
        zIndex: selected ? 20 : 10,
      }}
    >
      <div style={{
        background: KColors.overlay,
        border: `1px solid ${selected ? KColors.primary : KColors.border}`,
        borderRadius: 8,
        boxShadow: selected ? `0 0 0 2px ${KColors.primaryDim}` : 'none',
        transition: 'border-color 120ms, box-shadow 120ms',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{ background: pm.bg, borderBottom: `1px solid ${KColors.border}`, padding: '7px 10px', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: pm.color, flexShrink: 0 }}/>
          <span style={{ fontSize: 10, fontWeight: 600, color: pm.color, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{pm.label}</span>
        </div>
        {/* Body */}
        <div style={{ padding: '8px 10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
          <Port kind="input" nodeId={node.id} onPortMouseUp={onPortMouseUp} active={connectingFrom && connectingFrom !== node.id}/>
          <div style={{ flex: 1, minWidth: 0, textAlign: 'center' }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: KColors.fg1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.label}</div>
            <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 10, color: KColors.fg3, marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{node.type}</div>
          </div>
          <Port kind="output" nodeId={node.id} onPortMouseDown={onPortMouseDown} active={connectingFrom === node.id}/>
        </div>
      </div>
    </div>
  );
}

// ── Properties Panel ──────────────────────────────────
function PropertiesPanel({ node, nodes, edges, onParamChange, onDelete, onAddEdge, onRemoveEdge, onUpdateEdgeTrigger }) {
  const [targetNodeId, setTargetNodeId] = React.useState('');
  const connectionTargetSelectId = React.useId();
  React.useEffect(() => {
    setTargetNodeId('');
  }, [node?.id]);

  if (!node) return (
    <div style={{ width: 240, borderLeft: `1px solid ${KColors.border}`, padding: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 13, color: KColors.fg3, marginBottom: 6 }}>Select a node</div>
        <div style={{ fontSize: 11, color: KColors.fg3, lineHeight: 1.5 }}>Click a step on the canvas to edit its parameters.</div>
      </div>
    </div>
  );
  const pm = PROVIDER_META[node.provider] || PROVIDER_META.engine;
  const outgoingEdges = edges.filter(e => e.from === node.id);
  const connectedTargetIds = new Set(outgoingEdges.map(e => e.to));
  const availableTargets = nodes.filter(n => n.id !== node.id && !connectedTargetIds.has(n.id));
  return (
    <div style={{ width: 240, borderLeft: `1px solid ${KColors.border}`, padding: 16, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <KSectionLabel>Properties</KSectionLabel>
          <button onClick={onDelete} style={{ background: KColors.errorBg, color: KColors.error, border: `1px solid rgba(220,38,38,0.25)`, borderRadius: 4, padding: '3px 8px', fontSize: 11, fontWeight: 500, cursor: 'pointer', fontFamily: 'inherit' }}>Delete</button>
        </div>
        <div style={{ background: pm.bg, border: `1px solid rgba(255,255,255,0.06)`, borderRadius: 6, padding: '8px 10px', marginBottom: 10 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: pm.color }}>{node.label}</div>
          <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 10, color: KColors.fg3, marginTop: 2 }}>{node.type}</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <KSectionLabel>Parameters</KSectionLabel>
        {Object.entries(node.params).map(([key, val]) => (
          <KInput
            key={key}
            label={key}
            value={String(val)}
            onChange={v => onParamChange(node.id, key, v)}
          />
        ))}
        {Object.keys(node.params).length === 0 && (
          <div style={{ fontSize: 12, color: KColors.fg3 }}>No parameters.</div>
        )}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <KSectionLabel>Connections</KSectionLabel>
        <label
          htmlFor={connectionTargetSelectId}
          style={{ fontSize: 11, color: KColors.fg3, marginBottom: -4 }}
        >
          Target step
        </label>
        <div style={{ display: 'flex', gap: 6 }}>
          <select
            id={connectionTargetSelectId}
            value={targetNodeId}
            onChange={e => setTargetNodeId(e.target.value)}
            style={{
              flex: 1,
              background: KColors.overlay,
              color: KColors.fg1,
              border: `1px solid ${KColors.border}`,
              borderRadius: 6,
              padding: '6px 8px',
              fontSize: 12,
              outline: 'none',
              fontFamily: 'inherit',
            }}
          >
            <option value="">Select target step</option>
            {availableTargets.map(target => (
              <option key={target.id} value={target.id}>
                {target.label}
              </option>
            ))}
          </select>
          <KButton
            size="sm"
            onClick={() => {
              if (!targetNodeId) return;
              onAddEdge(node.id, targetNodeId);
              setTargetNodeId('');
            }}
            disabled={!targetNodeId}
          >
            Link
          </KButton>
        </div>
        {outgoingEdges.length === 0 ? (
          <div style={{ fontSize: 12, color: KColors.fg3 }}>No outgoing links.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {outgoingEdges.map(edge => {
              const target = nodes.find(n => n.id === edge.to);
              const triggerMode = edge.trigger?.mode || 'always';
              const triggerExpression = edge.trigger?.expression || '';
              return (
                <div
                  key={edge.id}
                  style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 6, padding: '6px 8px' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6 }}>
                    <div style={{ fontSize: 12, color: KColors.fg2, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      -> {target?.label || edge.to}
                    </div>
                    <button
                      onClick={() => onRemoveEdge(edge.id)}
                      aria-label={`Remove link to ${target?.label || edge.to}`}
                      style={{
                        background: 'transparent',
                        color: KColors.error,
                        border: `1px solid rgba(220,38,38,0.3)`,
                        borderRadius: 4,
                        padding: '2px 6px',
                        fontSize: 11,
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                      }}
                    >
                      Remove
                    </button>
                  </div>
                  <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                    <select
                      value={triggerMode}
                      onChange={e => onUpdateEdgeTrigger(edge.id, {
                        mode: e.target.value,
                        expression: e.target.value === 'conditional' ? triggerExpression : '',
                      })}
                      style={{
                        width: 110,
                        background: KColors.overlay,
                        color: KColors.fg1,
                        border: `1px solid ${KColors.border}`,
                        borderRadius: 6,
                        padding: '5px 6px',
                        fontSize: 11,
                        fontFamily: 'inherit',
                      }}
                    >
                      <option value="always">Always</option>
                      <option value="conditional">Conditional</option>
                    </select>
                    {triggerMode === 'conditional' && (
                      <input
                        value={triggerExpression}
                        onChange={e => onUpdateEdgeTrigger(edge.id, {
                          mode: 'conditional',
                          expression: e.target.value,
                        })}
                        placeholder="e.g. amount > 1000"
                        style={{
                          flex: 1,
                          background: KColors.overlay,
                          color: KColors.fg1,
                          border: `1px solid ${KColors.border}`,
                          borderRadius: 6,
                          padding: '5px 8px',
                          fontSize: 11,
                          fontFamily: 'IBM Plex Mono, monospace',
                        }}
                      />
                    )}
                  </div>
                  <div style={{ fontSize: 10, color: KColors.fg3, marginTop: 4 }}>
                    Trigger: {triggerMode === 'always' ? 'always on success' : (triggerExpression || 'conditional (set rule)')}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      <div style={{ marginTop: 'auto' }}>
        <div style={{ fontSize: 11, color: KColors.fg3, fontFamily: 'IBM Plex Mono, monospace' }}>id: {node.id}</div>
      </div>
    </div>
  );
}

// ── SVG Edges ─────────────────────────────────────────
function EdgeLayer({ nodes, edges, pendingEdge }) {
  function getPortPos(nodeId, kind) {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return { x: 0, y: 0 };
    const nodeW = 180, nodeH = 62;
    return {
      x: kind === 'output' ? node.x + nodeW - 5 : node.x + 5,
      y: node.y + nodeH / 2,
    };
  }

  function bezier(x1, y1, x2, y2) {
    const cx = (x1 + x2) / 2;
    return `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`;
  }

  return (
    <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 5 }}>
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill={KColors.primaryLight} opacity="0.7"/>
        </marker>
      </defs>
      {edges.map(edge => {
        const from = getPortPos(edge.from, 'output');
        const to   = getPortPos(edge.to,   'input');
        const triggerText = edge.trigger?.mode === 'conditional'
          ? (edge.trigger?.expression || '?')
          : 'always';
        const midX = (from.x + to.x) / 2;
        const midY = (from.y + to.y) / 2;
        return (
          <g key={edge.id}>
            <path d={bezier(from.x, from.y, to.x, to.y)}
              stroke={KColors.primaryLight} strokeWidth="1.5" fill="none" opacity="0.7"
              markerEnd="url(#arrowhead)"
            />
            <text
              x={midX}
              y={midY - 6}
              textAnchor="middle"
              style={{
                fill: KColors.fg3,
                fontSize: 10,
                fontFamily: 'IBM Plex Mono, monospace',
                userSelect: 'none',
              }}
            >
              {triggerText}
            </text>
          </g>
        );
      })}
      {pendingEdge && (
        <path d={bezier(pendingEdge.x1, pendingEdge.y1, pendingEdge.x2, pendingEdge.y2)}
          stroke={KColors.primary} strokeWidth="1.5" fill="none" opacity="0.5" strokeDasharray="5 3"
        />
      )}
    </svg>
  );
}

// ── Dot grid background ───────────────────────────────
function DotGrid() {
  return (
    <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
      <defs>
        <pattern id="dots" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill={KColors.border}/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dots)"/>
    </svg>
  );
}

// ── Main Builder ──────────────────────────────────────
function WorkflowBuilder() {
  const defaultDemoWorkflow = React.useMemo(() => buildDefaultDemoWorkflow(), []);
  const [nodes, setNodes] = React.useState(defaultDemoWorkflow.nodes);
  const [edges, setEdges] = React.useState(defaultDemoWorkflow.edges);
  const [selectedId, setSelectedId] = React.useState(null);
  const [draggingNode, setDraggingNode] = React.useState(null);
  const [draggingPalette, setDraggingPalette] = React.useState(null);
  const [connectingFrom, setConnectingFrom] = React.useState(null);
  const [pendingEdge, setPendingEdge] = React.useState(null);
  const [workflowName, setWorkflowName] = React.useState(defaultDemoWorkflow.workflowName);
  const [exported, setExported] = React.useState(false);
  const canvasRef = React.useRef(null);
  const suppressCanvasClickRef = React.useRef(false);

  const selectedNode = nodes.find(n => n.id === selectedId) || null;

  function suppressNextCanvasClick() {
    suppressCanvasClickRef.current = true;
    window.setTimeout(() => {
      suppressCanvasClickRef.current = false;
    }, 0);
  }

  function addNodeFromPalette(type) {
    const index = nodes.length;
    const x = 80 + (index % 3) * 220;
    const y = 90 + Math.floor(index / 3) * 110;
    const createdNode = makeNode(type, x, y);
    setNodes(prev => [...prev, createdNode]);
    setSelectedId(createdNode.id);
    suppressNextCanvasClick();
  }

  function handleNodeMouseDown(nodeId, e) {
    if (connectingFrom) return;
    e.stopPropagation();
    e.preventDefault();
    setSelectedId(nodeId);
    const node = nodes.find(n => n.id === nodeId);
    setDraggingNode({ id: nodeId, ox: e.clientX - node.x, oy: e.clientY - node.y });
  }

  function handlePortMouseDown(nodeId, e) {
    e.stopPropagation();
    e.preventDefault();
    setConnectingFrom(nodeId);
    const node = nodes.find(n => n.id === nodeId);
    const x1 = node.x + 175;
    const y1 = node.y + 31;
    setPendingEdge({ x1, y1, x2: e.clientX - canvasRef.current.getBoundingClientRect().left, y2: e.clientY - canvasRef.current.getBoundingClientRect().top });
  }

  function handlePortMouseUp(targetId) {
    if (connectingFrom && connectingFrom !== targetId) {
      const already = edges.find(e => e.from === connectingFrom && e.to === targetId);
      if (!already) {
        setEdges(prev => [...prev, makeEdge(connectingFrom, targetId)]);
      }
      suppressNextCanvasClick();
    }
    setConnectingFrom(null);
    setPendingEdge(null);
  }

  function handleNodeMouseUp(targetId) {
    handlePortMouseUp(targetId);
  }

  function handlePaletteDragStart(type, e) {
    e.preventDefault();
    setDraggingPalette({ type, curX: e.clientX, curY: e.clientY });
  }

  React.useEffect(() => {
    function onMove(e) {
      if (draggingNode) {
        setNodes(prev => prev.map(n => n.id === draggingNode.id
          ? { ...n, x: Math.max(0, e.clientX - draggingNode.ox), y: Math.max(0, e.clientY - draggingNode.oy) }
          : n
        ));
      }
      if (draggingPalette) {
        setDraggingPalette(p => ({ ...p, curX: e.clientX, curY: e.clientY }));
      }
      if (connectingFrom && canvasRef.current) {
        const r = canvasRef.current.getBoundingClientRect();
        const node = nodes.find(n => n.id === connectingFrom);
        if (node) {
          setPendingEdge({ x1: node.x + 175, y1: node.y + 31, x2: e.clientX - r.left, y2: e.clientY - r.top });
        }
      }
    }
    function onUp(e) {
      if (draggingNode) setDraggingNode(null);
      if (draggingPalette && canvasRef.current) {
        const r = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - r.left - 90;
        const y = e.clientY - r.top - 31;
        if (x > 0 && y > 0 && x < r.width - 180 && y < r.height - 62) {
          const createdNode = makeNode(draggingPalette.type, x, y);
          setNodes(prev => [...prev, createdNode]);
          setSelectedId(createdNode.id);
          suppressNextCanvasClick();
        }
        setDraggingPalette(null);
      }
      if (connectingFrom) {
        setConnectingFrom(null);
        setPendingEdge(null);
      }
    }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [draggingNode, draggingPalette, connectingFrom, nodes]);

  React.useEffect(() => {
    function onKey(e) {
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId && e.target === document.body) {
        deleteSelected();
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [selectedId]);

  function deleteSelected() {
    setNodes(prev => prev.filter(n => n.id !== selectedId));
    setEdges(prev => prev.filter(e => e.from !== selectedId && e.to !== selectedId));
    setSelectedId(null);
  }

  function handleParamChange(nodeId, key, val) {
    setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, params: { ...n.params, [key]: val } } : n));
  }

  function addEdge(fromId, toId) {
    if (!fromId || !toId || fromId === toId) return;
    setEdges(prev => {
      const duplicate = prev.some(e => e.from === fromId && e.to === toId);
      if (duplicate) return prev;
      return [...prev, makeEdge(fromId, toId)];
    });
  }

  function removeEdge(edgeId) {
    setEdges(prev => prev.filter(e => e.id !== edgeId));
  }

  function updateEdgeTrigger(edgeId, triggerPatch) {
    setEdges(prev => prev.map(edge => {
      if (edge.id !== edgeId) return edge;
      const nextMode = triggerPatch.mode || 'always';
      return {
        ...edge,
        trigger: {
          mode: nextMode,
          expression: nextMode === 'conditional' ? (triggerPatch.expression || '') : '',
        },
      };
    }));
  }

  function exportJSON() {
    const workflow = {
      workflow_name: workflowName,
      steps: nodes.map((n, i) => ({
        id: n.id, seq: i + 1, type: n.type, params: n.params,
        depends_on: edges.filter(e => e.to === n.id).map(e => e.from),
        outbound_triggers: edges
          .filter(e => e.from === n.id)
          .map(e => ({
            to: e.to,
            mode: e.trigger?.mode || 'always',
            expression: e.trigger?.mode === 'conditional' ? (e.trigger?.expression || '') : '',
          })),
      })),
    };
    return JSON.stringify(workflow, null, 2);
  }

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Step palette */}
      <div style={{ width: 200, borderRight: `1px solid ${KColors.border}`, overflow: 'auto', background: KColors.raised, flexShrink: 0 }}>
        <div style={{ padding: '12px 12px 8px', borderBottom: `1px solid ${KColors.border}` }}>
          <KSectionLabel>Step palette</KSectionLabel>
          <div style={{ fontSize: 11, color: KColors.fg3, lineHeight: 1.5 }}>Drag steps onto the canvas to build your workflow.</div>
        </div>
        {PROVIDERS_ORDER.map(provider => {
          const steps = STEP_CATALOG.filter(s => s.provider === provider);
          const pm = PROVIDER_META[provider];
          return (
            <div key={provider} style={{ padding: '10px 10px 6px' }}>
              <div style={{ fontSize: 10, fontWeight: 600, color: pm.color, letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: 6 }}>{pm.label}</div>
              {steps.map(step => (
                <div
                  key={step.type}
                  onMouseDown={e => handlePaletteDragStart(step.type, e)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      addNodeFromPalette(step.type);
                    }
                  }}
                  tabIndex={0}
                  role="button"
                  aria-label={`Add ${step.label} step`}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    padding: '7px 8px', borderRadius: 6, marginBottom: 4,
                    background: KColors.overlay, border: `1px solid ${KColors.border}`,
                    cursor: 'grab', userSelect: 'none',
                    transition: 'border-color 120ms, background 120ms',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = KColors.borderStrong; e.currentTarget.style.background = '#1e2130'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = KColors.border; e.currentTarget.style.background = KColors.overlay; }}
                >
                  <span style={{ width: 6, height: 6, borderRadius: '50%', background: pm.color, flexShrink: 0 }}/>
                  <span style={{ fontSize: 12, fontWeight: 500, color: KColors.fg1 }}>{step.label}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Canvas + toolbar */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Toolbar */}
        <div style={{ padding: '10px 16px', borderBottom: `1px solid ${KColors.border}`, display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0, background: KColors.raised }}>
          <input
            value={workflowName}
            onChange={e => setWorkflowName(e.target.value)}
            style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 13, background: 'transparent', border: 'none', color: KColors.fg1, outline: 'none', width: 200 }}
          />
          <span style={{ color: KColors.border }}>|</span>
          <span style={{ fontSize: 12, color: KColors.fg3 }}>{nodes.length} step{nodes.length !== 1 ? 's' : ''} · {edges.length} connection{edges.length !== 1 ? 's' : ''}</span>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
            {selectedId && (
              <KButton variant="danger" size="sm" onClick={deleteSelected}>Delete step</KButton>
            )}
            <KButton variant="secondary" size="sm" onClick={() => { setNodes([]); setEdges([]); setSelectedId(null); }}>Clear</KButton>
            <KButton size="sm" onClick={async () => {
              const json = exportJSON();
              try {
                if (navigator.clipboard?.writeText) {
                  await navigator.clipboard.writeText(json);
                }
              } catch {
                // Keep UI responsive even if clipboard permission is denied.
              }
              setExported(true);
              setTimeout(() => setExported(false), 2000);
            }}>
              {exported ? 'Copied!' : 'Export JSON'}
            </KButton>
          </div>
        </div>

        {/* Canvas area */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          <div
            ref={canvasRef}
            style={{ flex: 1, position: 'relative', overflow: 'hidden', background: KColors.sunken, cursor: connectingFrom ? 'crosshair' : 'default' }}
            onClick={() => {
              if (suppressCanvasClickRef.current) {
                suppressCanvasClickRef.current = false;
                return;
              }
              if (!draggingNode && !draggingPalette) setSelectedId(null);
            }}
          >
            <DotGrid/>
            <EdgeLayer nodes={nodes} edges={edges} pendingEdge={pendingEdge}/>
            {nodes.map(node => (
              <CanvasNode
                key={node.id}
                node={node}
                selected={selectedId === node.id}
                onMouseDown={handleNodeMouseDown}
                onPortMouseDown={handlePortMouseDown}
                onPortMouseUp={handlePortMouseUp}
                onNodeMouseUp={handleNodeMouseUp}
                connectingFrom={connectingFrom}
              />
            ))}
            {draggingPalette && (() => {
              const catalog = STEP_CATALOG.find(s => s.type === draggingPalette.type);
              const pm = PROVIDER_META[catalog?.provider] || PROVIDER_META.engine;
              return (
                <div style={{ position: 'fixed', left: draggingPalette.curX - 90, top: draggingPalette.curY - 20, width: 180, pointerEvents: 'none', opacity: 0.85, zIndex: 9999 }}>
                  <div style={{ background: KColors.overlay, border: `1px solid ${KColors.primary}`, borderRadius: 8, overflow: 'hidden' }}>
                    <div style={{ background: pm.bg, borderBottom: `1px solid ${KColors.border}`, padding: '7px 10px' }}>
                      <span style={{ fontSize: 10, fontWeight: 600, color: pm.color, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{pm.label}</span>
                    </div>
                    <div style={{ padding: '8px 10px', textAlign: 'center' }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: KColors.fg1 }}>{catalog?.label ?? draggingPalette.type}</div>
                    </div>
                  </div>
                </div>
              );
            })()}
            {nodes.length === 0 && (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 8, pointerEvents: 'none' }}>
                <div style={{ fontSize: 14, color: KColors.fg3 }}>Drag steps from the palette to start building.</div>
                <div style={{ fontSize: 12, color: KColors.fg3 }}>Connect nodes by dragging from the right port of one step to the left port of another.</div>
              </div>
            )}
          </div>

          {/* Right properties panel */}
          <PropertiesPanel
            node={selectedNode}
            nodes={nodes}
            edges={edges}
            onParamChange={handleParamChange}
            onDelete={deleteSelected}
            onAddEdge={addEdge}
            onRemoveEdge={removeEdge}
            onUpdateEdgeTrigger={updateEdgeTrigger}
          />
        </div>

        {/* Export preview bar */}
        {exported && (
          <div style={{ padding: '8px 16px', borderTop: `1px solid ${KColors.border}`, background: KColors.overlay, fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: KColors.fg2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {exportJSON().split('\n').slice(0, 3).join('  ')} …
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { WorkflowBuilder });
