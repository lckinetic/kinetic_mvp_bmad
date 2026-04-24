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

function simulateRun(steps, onStep, onDone) {
  let i = 0;
  const statuses = {};
  steps.forEach(s => { statuses[s] = 'pending'; });

  function next() {
    if (i >= steps.length) { onDone('completed', statuses); return; }
    statuses[steps[i]] = 'running';
    onStep({ ...statuses });
    const delay = 600 + Math.random() * 600;
    setTimeout(() => {
      statuses[steps[i]] = 'completed';
      onStep({ ...statuses });
      i++;
      setTimeout(next, 200);
    }, delay);
  }
  next();
}

function WorkflowRunner() {
  const [selectedTemplate, setSelectedTemplate] = React.useState(TEMPLATES[0]);
  const [inputs, setInputs] = React.useState(DEFAULT_INPUTS);
  const [runState, setRunState] = React.useState('idle'); // idle | running | done
  const [stepStatuses, setStepStatuses] = React.useState({});
  const [stepRows, setStepRows] = React.useState([]);
  const [runId] = React.useState(() => Math.random().toString(36).slice(2,10));

  const tmpl = selectedTemplate;

  function handleRun() {
    if (runState === 'running') return;
    setRunState('running');
    const init = {};
    tmpl.step_outline.forEach(s => { init[s] = 'pending'; });
    setStepStatuses(init);
    setStepRows([]);

    const durations = {};

    simulateRun(
      tmpl.step_outline,
      (statuses) => {
        setStepStatuses({ ...statuses });
        const rows = tmpl.step_outline.map((name, idx) => {
          const st = statuses[name];
          if (st === 'completed' && !durations[name]) durations[name] = Math.round(300 + Math.random() * 700);
          return { seq: idx + 1, step_name: name, status: st, duration_ms: durations[name] ?? null };
        });
        setStepRows(rows);
      },
      () => {
        setRunState('done');
      }
    );
  }

  const totalDone = Object.values(stepStatuses).filter(s => s === 'completed').length;
  const pct = tmpl.step_outline.length ? Math.round((totalDone / tmpl.step_outline.length) * 100) : 0;
  const overallStatus = runState === 'idle' ? null : runState === 'running' ? 'running' : 'completed';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', height: '100%', overflow: 'hidden' }}>
      {/* Left panel */}
      <div style={{ borderRight: `1px solid ${KColors.border}`, padding: 20, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div>
          <KSectionLabel>Template</KSectionLabel>
          <KSelect
            options={TEMPLATES.map(t => ({ value: t.name, label: t.display_name }))}
            value={tmpl.name}
            onChange={name => {
              setSelectedTemplate(TEMPLATES.find(t => t.name === name));
              setRunState('idle'); setStepStatuses({}); setStepRows([]);
            }}
          />
          <div style={{ marginTop: 10, padding: 12, background: KColors.overlay, borderRadius: 8, border: `1px solid ${KColors.border}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: KColors.fg1 }}>{tmpl.display_name}</span>
              <KPill status="default">v{tmpl.version}</KPill>
            </div>
            <div style={{ fontSize: 12, color: KColors.fg3 }}>{tmpl.description}</div>
            <div style={{ marginTop: 6, fontSize: 11, color: KColors.fg3, fontFamily: 'IBM Plex Mono, monospace', letterSpacing: '0.02em' }}>
              {tmpl.category.toUpperCase()}
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
      </div>

      {/* Right panel */}
      <div style={{ padding: 24, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Overview */}
        <div>
          <KSectionLabel>Workflow overview</KSectionLabel>
          <div style={{ fontSize: 14, fontWeight: 600, color: KColors.fg1, marginBottom: 4 }}>{tmpl.business_summary}</div>
          <ol style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 3 }}>
            {tmpl.business_steps.map((s,i) => <li key={i} style={{ fontSize: 13, color: KColors.fg2 }}>{s}</li>)}
          </ol>
        </div>

        <KDivider/>

        {/* Progress */}
        <div>
          <KSectionLabel>Progress</KSectionLabel>
          <KStepper steps={tmpl.step_outline.map(k => tmpl.step_labels[k] || k)} statuses={
            Object.fromEntries(tmpl.step_outline.map((k) => [tmpl.step_labels[k] || k, stepStatuses[k] || 'pending']))
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
              template: tmpl.name,
              run_id: runId,
              status: 'completed',
              steps: tmpl.step_outline.map(s => ({ step: s, status: 'completed' })),
            }, null, 2)} minHeight={140}/>
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { WorkflowRunner });
