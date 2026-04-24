// Kinetic — AI Workflow Generator Screen

const EXAMPLE_PROMPTS = [
  'Buy BTC and withdraw to wallet',
  'Create a wallet for me',
  'Fund wallet with USDC',
];

const MOCK_WORKFLOWS = {
  'Buy BTC and withdraw to wallet': {
    workflow_name: 'buy_btc_withdraw',
    business_summary: 'Buy Bitcoin on the exchange and withdraw it to a destination wallet.',
    steps: [
      { id: 'step_1', type: 'coinbase.buy',      params: { asset: 'BTC', amount: 100, currency: 'USD' } },
      { id: 'step_2', type: 'coinbase.withdraw',  params: { asset: 'BTC', destination: '0xWALLET' } },
    ],
  },
  'Create a wallet for me': {
    workflow_name: 'create_wallet',
    business_summary: 'Provision a new custodial wallet via the Privy adapter.',
    steps: [
      { id: 'step_1', type: 'privy.create_wallet', params: { chain: 'ethereum' } },
    ],
  },
  'Fund wallet with USDC': {
    workflow_name: 'fund_wallet_usdc',
    business_summary: 'On-ramp fiat to USDC and deliver to an existing wallet.',
    steps: [
      { id: 'step_1', type: 'banxa.onramp',  params: { fiat_amount: 500, fiat_currency: 'USD', crypto_currency: 'USDC' } },
      { id: 'step_2', type: 'privy.deposit', params: { asset: 'USDC', destination: '0xWALLET' } },
    ],
  },
};

function getFallbackWorkflow(prompt) {
  return {
    workflow_name: 'custom_workflow',
    business_summary: `Execute: "${prompt}"`,
    steps: [
      { id: 'step_1', type: 'engine.interpret', params: { prompt, model: 'gpt-4o' } },
      { id: 'step_2', type: 'engine.execute',   params: { dry_run: false } },
    ],
  };
}

function simulateAIRun(steps, onStep, onDone) {
  let i = 0;
  const durations = {};
  function next() {
    if (i >= steps.length) { onDone(); return; }
    onStep(i, 'running', durations);
    const delay = 500 + Math.random() * 700;
    setTimeout(() => {
      durations[i] = Math.round(300 + Math.random() * 600);
      onStep(i, 'completed', durations);
      i++;
      setTimeout(next, 200);
    }, delay);
  }
  next();
}

function StepCard({ step, idx }) {
  return (
    <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 8, padding: 12, marginBottom: 8 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: KColors.fg3, marginBottom: 4 }}>Step {idx + 1}</div>
      <div style={{ fontSize: 13, fontWeight: 600, color: KColors.primaryLight, marginBottom: 6 }}>{step.type}</div>
      <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: KColors.fg2, background: KColors.sunken, padding: '8px 10px', borderRadius: 4, border: `1px solid ${KColors.border}` }}>
        {JSON.stringify(step.params || {}, null, 2)}
      </div>
    </div>
  );
}

function AIGenerator() {
  const [prompt, setPrompt] = React.useState('');
  const [genState, setGenState] = React.useState('idle'); // idle | generating | ready
  const [runState, setRunState] = React.useState('idle'); // idle | running | done
  const [workflow, setWorkflow] = React.useState(null);
  const [workflowJson, setWorkflowJson] = React.useState('{}');
  const [stepStatuses, setStepStatuses] = React.useState([]);
  const [runSummary, setRunSummary] = React.useState(null);
  const [runId] = React.useState(() => Math.random().toString(36).slice(2,10));

  function handleGenerate() {
    if (!prompt.trim() || genState === 'generating') return;
    setGenState('generating');
    setWorkflow(null);
    setRunState('idle');
    setStepStatuses([]);
    setRunSummary(null);

    setTimeout(() => {
      const wf = MOCK_WORKFLOWS[prompt.trim()] || getFallbackWorkflow(prompt.trim());
      setWorkflow(wf);
      setWorkflowJson(JSON.stringify(wf, null, 2));
      setStepStatuses(wf.steps.map(() => ({ status: 'pending', duration_ms: null })));
      setGenState('ready');
    }, 1200);
  }

  function handleRun() {
    if (runState === 'running' || genState !== 'ready') return;
    let wf;
    try { wf = JSON.parse(workflowJson); } catch { return; }
    setRunState('running');
    const initStatuses = wf.steps.map(() => ({ status: 'pending', duration_ms: null }));
    setStepStatuses(initStatuses);

    simulateAIRun(
      wf.steps,
      (i, status, durations) => {
        setStepStatuses(prev => prev.map((s, idx) => {
          if (idx < i) return { status: 'completed', duration_ms: durations[idx] ?? s.duration_ms };
          if (idx === i) return { status, duration_ms: durations[idx] ?? null };
          return s;
        }));
      },
      () => {
        setRunState('done');
        setRunSummary({ status: 'completed', duration_ms: Math.round(800 + Math.random() * 1200) });
      }
    );
  }

  const currentWorkflow = (() => { try { return JSON.parse(workflowJson); } catch { return null; } })();

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', height: '100%', overflow: 'hidden' }}>
      {/* Left panel */}
      <div style={{ borderRight: `1px solid ${KColors.border}`, padding: 20, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <div>
          <KSectionLabel>Your request</KSectionLabel>
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder="Describe the financial workflow you want…"
            onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleGenerate(); }}
            style={{
              fontFamily: 'inherit', fontSize: 14, width: '100%', minHeight: 100,
              padding: '10px 12px', boxSizing: 'border-box', resize: 'vertical',
              background: KColors.sunken, color: KColors.fg1,
              border: `1px solid ${KColors.borderStrong}`, borderRadius: 4, outline: 'none',
            }}
          />
          <div style={{ marginTop: 8 }}>
            <div style={{ fontSize: 11, color: KColors.fg3, marginBottom: 6 }}>Try an example:</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {EXAMPLE_PROMPTS.map(p => (
                <button key={p} onClick={() => setPrompt(p)}
                  style={{ fontSize: 11, padding: '4px 10px', borderRadius: 9999, background: 'transparent', color: KColors.fg2, border: `1px solid ${KColors.borderStrong}`, cursor: 'pointer', fontFamily: 'inherit', transition: 'border-color 120ms ease-out, color 120ms ease-out' }}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <KButton onClick={handleGenerate} disabled={genState === 'generating' || !prompt.trim()} style={{ flex: 1, justifyContent: 'center' }}>
            {genState === 'generating' ? 'Generating…' : 'Generate workflow'}
          </KButton>
          <KButton variant="secondary" onClick={handleRun} disabled={genState !== 'ready' || runState === 'running'} style={{ flex: 1, justifyContent: 'center' }}>
            {runState === 'running' ? 'Running…' : 'Run workflow'}
          </KButton>
        </div>

        {/* Workflow card */}
        {workflow && (
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 8, padding: 14 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: KColors.fg1, marginBottom: 4 }}>{workflow.workflow_name}</div>
            <div style={{ fontSize: 12, color: KColors.fg3, marginBottom: 10 }}>{workflow.business_summary}</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              <KPill status="default">{workflow.steps.length} step{workflow.steps.length !== 1 ? 's' : ''}</KPill>
              {[...new Set(workflow.steps.map(s => s.type.split('.')[0]))].map(t => (
                <span key={t} style={{ display: 'inline-flex', padding: '3px 9px', borderRadius: 9999, background: KColors.primaryDim, color: KColors.primaryLight, fontSize: 11, fontWeight: 500 }}>{t}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right panel */}
      <div style={{ padding: 24, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {genState === 'idle' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 200, gap: 8 }}>
            <div style={{ fontSize: 14, color: KColors.fg3 }}>Describe a workflow to get started.</div>
          </div>
        )}

        {genState === 'generating' && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 200, gap: 8 }}>
            <div style={{ fontSize: 14, color: KColors.fg2 }}>Generating workflow…</div>
          </div>
        )}

        {(genState === 'ready') && workflow && (
          <>
            <div>
              <KSectionLabel>Generated steps</KSectionLabel>
              {workflow.steps.map((step, idx) => <StepCard key={step.id} step={step} idx={idx}/>)}
            </div>

            <div>
              <KSectionLabel>Generated JSON (editable)</KSectionLabel>
              <KCodeBlock value={workflowJson} onChange={setWorkflowJson} minHeight={180}/>
            </div>

            {runState !== 'idle' && (
              <>
                <div>
                  <KSectionLabel>Execution steps</KSectionLabel>
                  <KStepsTable steps={
                    (currentWorkflow?.steps || workflow.steps).map((s, i) => ({
                      seq: i + 1,
                      step_name: s.type,
                      status: stepStatuses[i]?.status || 'pending',
                      duration_ms: stepStatuses[i]?.duration_ms ?? null,
                    }))
                  }/>
                </div>

                {runSummary && (
                  <div style={{ padding: 12, background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 8, display: 'flex', alignItems: 'center', gap: 16 }}>
                    <KPill status="completed">completed</KPill>
                    <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>Run ID: {runId}</span>
                    <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>{runSummary.duration_ms} ms</span>
                  </div>
                )}

                {runState === 'done' && (
                  <div>
                    <KSectionLabel>Output</KSectionLabel>
                    <KCodeBlock readOnly value={JSON.stringify({
                      run_id: runId,
                      workflow_name: workflow.workflow_name,
                      status: 'completed',
                      output: { steps_executed: workflow.steps.length, duration_ms: runSummary?.duration_ms },
                    }, null, 2)} minHeight={120}/>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { AIGenerator });
