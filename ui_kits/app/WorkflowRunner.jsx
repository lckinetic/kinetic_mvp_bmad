// Kinetic — Workflow Runner Screen

const TEMPLATES = [
  {
    name: 'treasury_demo',
    display_name: 'Treasury Rebalance (Demo)',
    version: '1.0',
    category: 'treasury',
    description: 'Mock flow: Onramp → Complete → Offramp → Complete',
    business_summary: 'Convert fiat to stablecoins and back again using a pre-defined treasury workflow (demo).',
    business_steps: [
      'Buy stablecoins using a fiat onramp',
      'Confirm completion (provider status update)',
      'Sell stablecoins back to fiat (offramp)',
      'Confirm payout completion',
    ],
    step_outline: ['onramp.create','onramp.complete','offramp.create','offramp.complete'],
    step_labels: {
      'onramp.create':    'Buy stablecoins',
      'onramp.complete':  'Confirm purchase',
      'offramp.create':   'Sell stablecoins',
      'offramp.complete': 'Confirm payout',
    },
  },
  {
    name: 'managed_treasury',
    display_name: 'Managed Crypto Treasury',
    version: '1.0',
    category: 'treasury',
    description: 'Wallet → Trade → Withdraw',
    business_summary: 'Fund a wallet, trade assets, and withdraw to destination.',
    business_steps: [
      'Create or fund a custody wallet',
      'Execute a trade on the exchange',
      'Withdraw funds to destination address',
    ],
    step_outline: ['wallet.create','trade.execute','wallet.withdraw'],
    step_labels: {
      'wallet.create':   'Create wallet',
      'trade.execute':   'Execute trade',
      'wallet.withdraw': 'Withdraw funds',
    },
  },
];

const DEFAULT_INPUTS = {
  fiat_amount: '1000',
  fiat_currency: 'GBP',
  crypto_currency: 'USDC',
  wallet_address: '0xDEMO',
  blockchain: 'ethereum',
  user_email: 'demo@example.com',
  crypto_amount: '100',
  destination_reference: 'demo-bank-001',
};

const API_BASE = window.KINETIC_API_BASE || '';

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

function WorkflowRunner({ initialTemplateName = null }) {
  const [templates, setTemplates] = React.useState(TEMPLATES);
  const [selectedTemplate, setSelectedTemplate] = React.useState(TEMPLATES[0]);
  const [inputs, setInputs] = React.useState(DEFAULT_INPUTS);
  const [runState, setRunState] = React.useState('idle'); // idle | running | done
  const [stepStatuses, setStepStatuses] = React.useState({});
  const [stepRows, setStepRows] = React.useState([]);
  const [runId, setRunId] = React.useState('');
  const [apiError, setApiError] = React.useState('');

  const tmpl = selectedTemplate || templates[0] || TEMPLATES[0] || null;
  const templateName = String(tmpl?.name || "");
  const templateDisplayName = String(tmpl?.display_name || tmpl?.name || "Workflow template");
  const templateVersion = String(tmpl?.version || "1.0");
  const templateDescription = String(tmpl?.description || "No template description provided.");
  const templateCategory = String(tmpl?.category || "workflow");
  const businessSummary = String(tmpl?.business_summary || "Run a workflow template.");
  const stepOutline = Array.isArray(tmpl?.step_outline) ? tmpl.step_outline : [];
  const stepLabels = tmpl?.step_labels || {};
  const businessSteps = Array.isArray(tmpl?.business_steps) ? tmpl.business_steps : [];

  React.useEffect(() => {
    let cancelled = false;
    async function loadTemplates() {
      try {
        const rows = await apiGet('/workflows/templates');
        if (cancelled || !Array.isArray(rows) || rows.length === 0) return;
        setTemplates(rows);
        const preferred = initialTemplateName
          ? rows.find(t => t.name === initialTemplateName)
          : null;
        setSelectedTemplate(preferred || rows[0]);
      } catch {
        // Keep deterministic fallback templates when API is unavailable.
      }
    }
    loadTemplates();
    return () => { cancelled = true; };
  }, [initialTemplateName]);

  React.useEffect(() => {
    if (!initialTemplateName) return;
    const found = templates.find(t => t.name === initialTemplateName);
    if (found) setSelectedTemplate(found);
  }, [initialTemplateName, templates]);

  async function loadSteps(run) {
    try {
      const rows = await apiGet(`/workflows/runs/${run.id}/steps`);
      if (Array.isArray(rows) && rows.length) {
        setStepRows(rows);
        const statuses = {};
        rows.forEach(r => { statuses[r.step_name] = r.status; });
        setStepStatuses(statuses);
        return;
      }
    } catch {
      // Fall back to summary status.
    }
    const fallback = {};
    stepOutline.forEach(s => { fallback[s] = run.status === 'failed' ? 'failed' : 'completed'; });
    setStepStatuses(fallback);
    setStepRows(stepOutline.map((name, idx) => ({
      seq: idx + 1,
      step_name: name,
      status: fallback[name],
      duration_ms: null,
    })));
  }

  async function handleRun() {
    if (runState === 'running') return;
    if (!templateName) return;
    setApiError('');
    setRunState('running');
    const init = {};
    stepOutline.forEach(s => { init[s] = 'pending'; });
    setStepStatuses(init);
    setStepRows([]);
    try {
      const run = await apiPost(`/workflows/run/${templateName}`, { input: inputs });
      setRunId(String(run.id));
      await loadSteps(run);
      setRunState('done');
    } catch {
      setApiError('Unable to run workflow API. Showing fallback simulation.');
      const durations = {};
      stepOutline.forEach((name, idx) => {
        durations[name] = 350 + idx * 120;
      });
      const rows = stepOutline.map((name, idx) => ({
        seq: idx + 1,
        step_name: name,
        status: 'completed',
        duration_ms: durations[name],
      }));
      setStepRows(rows);
      const statuses = {};
      rows.forEach(r => { statuses[r.step_name] = r.status; });
      setStepStatuses(statuses);
      setRunId(Math.random().toString(36).slice(2, 10));
      setRunState('done');
    }
  }

  const totalDone = Object.values(stepStatuses).filter(s => s === 'completed').length;
  const pct = stepOutline.length ? Math.round((totalDone / stepOutline.length) * 100) : 0;
  const overallStatus = runState === 'idle' ? null : runState === 'running' ? 'running' : 'completed';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', height: '100%', overflow: 'hidden' }}>
      {/* Left panel */}
      <div style={{ borderRight: `1px solid ${KColors.border}`, padding: 20, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <KSectionLabel>Template</KSectionLabel>
          <KSelect
            options={templates.map(t => ({ value: t.name, label: t.display_name }))}
            value={templateName}
            onChange={name => {
              setSelectedTemplate(templates.find(t => t.name === name) || templates[0] || TEMPLATES[0]);
              setRunState('idle'); setStepStatuses({}); setStepRows([]);
            }}
          />
          <div style={{ marginTop: 10, padding: 12, background: KColors.overlay, borderRadius: 8, border: `1px solid ${KColors.border}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: KColors.fg1 }}>{templateDisplayName}</span>
              <KPill status="default">v{templateVersion}</KPill>
            </div>
            <div style={{ fontSize: 12, color: KColors.fg3 }}>{templateDescription}</div>
            <div style={{ marginTop: 6, fontSize: 11, color: KColors.fg3, fontFamily: 'IBM Plex Mono, monospace', letterSpacing: '0.02em' }}>
              {templateCategory.toUpperCase()}
            </div>
          </div>
        </div>

        <KDivider/>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <KSectionLabel>Inputs</KSectionLabel>
          <KInput label="Fiat amount" type="number" value={inputs.fiat_amount} onChange={v => setInputs(p => ({...p, fiat_amount: v}))} min={10} hint="Minimum 10"/>
          <KSelect label="Fiat currency" options={['GBP','EUR','USD']} value={inputs.fiat_currency} onChange={v => setInputs(p => ({...p, fiat_currency: v}))}/>
          <KSelect label="Crypto currency" options={['USDC','USDT','BTC','ETH']} value={inputs.crypto_currency} onChange={v => setInputs(p => ({...p, crypto_currency: v}))}/>
          <KInput label="Destination wallet" value={inputs.wallet_address} onChange={v => setInputs(p => ({...p, wallet_address: v}))} placeholder="0x…"/>
          <KSelect label="Blockchain" options={['ethereum','polygon','arbitrum']} value={inputs.blockchain} onChange={v => setInputs(p => ({...p, blockchain: v}))}/>
          <KInput label="User email" type="email" value={inputs.user_email} onChange={v => setInputs(p => ({...p, user_email: v}))} placeholder="name@company.com"/>
        </div>

        <KButton onClick={handleRun} disabled={runState === 'running'} style={{ width: '100%', justifyContent: 'center' }}>
          {runState === 'running' ? 'Running…' : 'Run workflow'}
        </KButton>
        {apiError && <div style={{ fontSize: 11, color: KColors.warning }}>{apiError}</div>}
      </div>

      {/* Right panel */}
      <div style={{ padding: 24, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Overview */}
        <div>
          <KSectionLabel>Workflow overview</KSectionLabel>
          <div style={{ fontSize: 14, fontWeight: 600, color: KColors.fg1, marginBottom: 4 }}>{businessSummary}</div>
          {businessSteps.length > 0 ? (
            <ol style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 3 }}>
              {businessSteps.map((s,i) => <li key={i} style={{ fontSize: 13, color: KColors.fg2 }}>{s}</li>)}
            </ol>
          ) : (
            <div style={{ fontSize: 13, color: KColors.fg2 }}>No business steps provided for this template.</div>
          )}
        </div>

        <KDivider/>

        {/* Progress */}
        <div>
          <KSectionLabel>Progress</KSectionLabel>
          <KStepper steps={stepOutline.map(k => stepLabels[k] || k)} statuses={
            Object.fromEntries(stepOutline.map((k) => [stepLabels[k] || k, stepStatuses[k] || 'pending']))
          }/>
        </div>

        {/* Run summary */}
        {runState !== 'idle' && (
          <div style={{ padding: 12, background: KColors.overlay, borderRadius: 8, border: `1px solid ${KColors.border}`, display: 'flex', alignItems: 'center', gap: 16 }}>
            <KPill status={overallStatus}>{overallStatus}</KPill>
            <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>Run ID: {runId}</span>
            <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>Progress: {pct}%</span>
          </div>
        )}

        {/* Steps */}
        <div>
          <KSectionLabel>Steps</KSectionLabel>
          {runState === 'idle'
            ? <div style={{ fontSize: 13, color: KColors.fg3 }}>Run the workflow to see steps.</div>
            : <KStepsTable steps={stepRows}/>
          }
        </div>

        {/* Output */}
        {runState === 'done' && (
          <div>
            <KSectionLabel>Output</KSectionLabel>
            <KCodeBlock readOnly value={JSON.stringify({
              template: templateName,
              template_display_name: templateDisplayName,
              run_id: runId,
              status: overallStatus || 'completed',
              steps: stepRows.map(s => ({ step: s.step_name, status: s.status })),
            }, null, 2)} minHeight={140}/>
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { WorkflowRunner });
