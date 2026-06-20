// Workflows and Activity Centre shells

const PAYOUT_WORKFLOWS_API = `${window.KINETIC_API_BASE || ''}/payout-workflows`;

const SCHEDULE_OPTIONS = [
  { value: 'manual', label: 'Manual only' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const WEEKDAY_OPTIONS = [
  { value: 'monday', label: 'Monday' },
  { value: 'tuesday', label: 'Tuesday' },
  { value: 'wednesday', label: 'Wednesday' },
  { value: 'thursday', label: 'Thursday' },
  { value: 'friday', label: 'Friday' },
];

const CONTRACTOR_PAYOUT_STEP_LABELS = {
  'balance.check': 'Checking treasury balance',
  'transfer.payout': 'Sending payout to contractor',
  'payout.complete': 'Completing payout run',
};

function payoutRunBusinessSteps(runPayload) {
  const steps = runPayload?.output?.steps;
  if (Array.isArray(steps) && steps.length) {
    return steps.map((step, index) => ({
      key: step.step || `step-${index}`,
      label: CONTRACTOR_PAYOUT_STEP_LABELS[step.step] || step.step || `Step ${index + 1}`,
    }));
  }
  return Object.entries(CONTRACTOR_PAYOUT_STEP_LABELS).map(([key, label]) => ({ key, label }));
}

function formatLastRun(iso) {
  if (!iso) return 'Never';
  return new Date(iso).toLocaleString();
}

async function payoutWorkflowRequest(path, options = {}) {
  const res = await fetch(`${PAYOUT_WORKFLOWS_API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body.message || 'Payout workflow request failed');
    err.code = body.code;
    err.details = body.details;
    throw err;
  }
  return body;
}

function emptyWorkflowForm() {
  return { name: '', recipient: null, amount: '500', schedule_cadence: 'manual', schedule_day: 'friday' };
}

function applyRecipientDefaults(recipient, prevForm) {
  if (!recipient || typeof recipient !== 'object') {
    return { ...prevForm, recipient: null };
  }
  return {
    ...prevForm,
    recipient,
    name: prevForm.name || `${recipient.name} payout`,
    amount: recipient.default_payout_amount != null ? String(recipient.default_payout_amount) : prevForm.amount,
    schedule_cadence: recipient.default_schedule_cadence || prevForm.schedule_cadence,
    schedule_day: recipient.default_schedule_day || prevForm.schedule_day || 'friday',
  };
}

function WorkflowsShell({ onNavigate, onChecklistStep }) {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState('');
  const [modalOpen, setModalOpen] = React.useState(false);
  const [editing, setEditing] = React.useState(null);
  const [form, setForm] = React.useState(emptyWorkflowForm());
  const [formError, setFormError] = React.useState('');
  const [runResult, setRunResult] = React.useState(null);
  const [recoveryRow, setRecoveryRow] = React.useState(null);

  const loadWorkflows = React.useCallback(async () => {
    setError('');
    try {
      const body = await payoutWorkflowRequest('');
      const rows = body.items || [];
      setItems(rows);
      if (onChecklistStep && rows.length > 0) onChecklistStep('workflow');
      return rows;
    } catch (err) {
      setError(err.message || 'Could not load payout workflows.');
      return [];
    }
  }, [onChecklistStep]);

  React.useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      await loadWorkflows();
      if (!cancelled) setLoading(false);
    }
    boot();
    return () => { cancelled = true; };
  }, [loadWorkflows]);

  React.useEffect(() => {
    if (window.lucide) lucide.createIcons();
  });

  function openCreateModal() {
    setEditing(null);
    setForm(emptyWorkflowForm());
    setFormError('');
    setModalOpen(true);
  }

  function openEditModal(row) {
    setEditing(row);
    setForm({
      name: row.name,
      recipient: row.recipient,
      amount: String(row.amount),
      schedule_cadence: row.schedule_cadence,
      schedule_day: row.schedule_day || 'friday',
    });
    setFormError('');
    setModalOpen(true);
  }

  async function handleSave() {
    setBusy(true);
    setFormError('');
    const amount = Number(form.amount);
    if (!form.name.trim() || !form.recipient || !Number.isFinite(amount) || amount <= 0) {
      setFormError('Name, recipient, and a valid amount are required.');
      setBusy(false);
      return;
    }
    const payload = {
      name: form.name.trim(),
      recipient_id: form.recipient.id,
      amount,
      schedule_cadence: form.schedule_cadence,
      schedule_day: form.schedule_cadence === 'manual' ? null : form.schedule_day,
    };
    try {
      if (editing) {
        await payoutWorkflowRequest(`/${editing.id}`, { method: 'PATCH', body: JSON.stringify(payload) });
      } else {
        await payoutWorkflowRequest('', { method: 'POST', body: JSON.stringify(payload) });
      }
      setModalOpen(false);
      await loadWorkflows();
    } catch (err) {
      setFormError(err.message || 'Could not save payout workflow.');
    } finally {
      setBusy(false);
    }
  }

  async function handleToggle(row) {
    setBusy(true);
    setError('');
    try {
      await payoutWorkflowRequest(`/${row.id}/${row.enabled ? 'disable' : 'enable'}`, { method: 'POST', body: '{}' });
      await loadWorkflows();
    } catch (err) {
      setError(err.message || 'Could not update workflow status.');
    } finally {
      setBusy(false);
    }
  }

  async function handleRun(row) {
    setBusy(true);
    setError('');
    setRunResult(null);
    setRecoveryRow(null);
    try {
      const result = await payoutWorkflowRequest(`/${row.id}/run`, { method: 'POST', body: '{}' });
      setRunResult(result);
      if (result.run?.status === 'completed' && onChecklistStep) onChecklistStep('firstRun');
      await loadWorkflows();
    } catch (err) {
      if (err.code === 'INSUFFICIENT_BALANCE') {
        setError(`${err.message} Fund treasury before retrying.`);
      } else if (err.code === 'PAYOUT_WORKFLOW_DISABLED') {
        setRecoveryRow(row);
        setError(`${err.message} Enable the workflow before running again.`);
      } else if (err.code === 'RECIPIENT_INACTIVE') {
        setError(`${err.message} Reactivate or update the recipient before retrying.`);
      } else {
        setError(err.message || 'Payout run failed.');
      }
    } finally {
      setBusy(false);
    }
  }

  const enabledCount = items.filter(row => row.enabled).length;

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Workflows</div>
          <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>
            Contractor payout workflows · {enabledCount} enabled
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <KButton onClick={openCreateModal}>Create payout workflow</KButton>
          <KButton variant="ghost" size="sm" onClick={() => onNavigate('templates')}>Legacy templates</KButton>
        </div>
      </div>

      {error && (
        <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.errorBg, border: '1px solid rgba(220,38,38,0.3)', color: KColors.error, fontSize: 13 }}>
          {error}
          {error.toLowerCase().includes('fund treasury') && (
            <div style={{ marginTop: 8 }}>
              <KButton size="sm" onClick={() => onNavigate('treasury')}>Fund treasury</KButton>
            </div>
          )}
          {error.toLowerCase().includes('enable the workflow') && recoveryRow && (
            <div style={{ marginTop: 8 }}>
              <KButton size="sm" onClick={() => handleToggle(recoveryRow)}>Enable workflow</KButton>
            </div>
          )}
          {(error.toLowerCase().includes('recipient') && error.toLowerCase().includes('inactive')) && (
            <div style={{ marginTop: 8 }}>
              <KButton size="sm" onClick={() => onNavigate('recipients')}>Edit recipient</KButton>
            </div>
          )}
        </div>
      )}

      {runResult && (
        <div style={{ padding: '12px 14px', borderRadius: 8, background: KColors.successBg, border: '1px solid rgba(22,163,74,0.35)', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: KColors.success }}>Payout run completed</div>
          <div style={{ fontSize: 12, color: KColors.fg2 }}>
            Run #{runResult.run.id} · {runResult.workflow.recipient?.name} · {runResult.workflow.amount} {runResult.workflow.asset}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {payoutRunBusinessSteps(runResult.run).map((step, index) => (
              <div key={step.key} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: KColors.fg2 }}>
                <span style={{ width: 18, height: 18, borderRadius: 9999, background: KColors.successBg, color: KColors.success, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, border: `1px solid rgba(22,163,74,0.35)` }}>{index + 1}</span>
                <span>{step.label}</span>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <KButton size="sm" variant="secondary" onClick={() => onNavigate('treasury')}>View treasury</KButton>
            <KButton size="sm" variant="ghost" onClick={() => onNavigate('activity')}>Activity Centre</KButton>
          </div>
        </div>
      )}

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr 0.65fr 0.75fr 0.95fr 1fr', gap: 8, padding: '10px 14px', borderBottom: `1px solid ${KColors.border}`, fontSize: 11, fontWeight: 600, color: KColors.fg3, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          <span>Name</span><span>Recipient</span><span>Amount</span><span>Schedule</span><span>Last run</span><span>Actions</span>
        </div>

        {loading ? (
          <div style={{ padding: 20, fontSize: 13, color: KColors.fg3 }}>Loading payout workflows…</div>
        ) : items.length === 0 ? (
          <KEmptyState
            icon="git-branch"
            title="No payout workflows configured"
            description="Create a contractor payout workflow to pay recipients from treasury with balance guardrails and step-level visibility."
            actionLabel="Create payout workflow"
            onAction={openCreateModal}
            secondaryLabel="Manage recipients"
            onSecondary={() => onNavigate('recipients')}
          />
        ) : (
          items.map(row => (
            <div key={row.id} style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr 0.65fr 0.75fr 0.95fr 1fr', gap: 8, padding: '12px 14px', borderBottom: `1px solid ${KColors.border}`, alignItems: 'center', fontSize: 13 }}>
              <div>
                <div style={{ color: KColors.fg1, fontWeight: 600 }}>{row.name}</div>
                <div style={{ marginTop: 4 }}><KPill status={row.enabled ? 'completed' : 'pending'}>{row.enabled ? 'enabled' : 'disabled'}</KPill></div>
              </div>
              <span style={{ color: KColors.fg2 }}>{row.recipient?.name || '—'}</span>
              <span style={{ fontFamily: 'IBM Plex Mono, monospace', color: KColors.fg1 }}>{row.amount} {row.asset}</span>
              <span style={{ color: KColors.fg3, fontSize: 12 }}>{row.schedule_label}</span>
              <span style={{ color: KColors.fg3, fontSize: 12, whiteSpace: 'nowrap' }}>{formatLastRun(row.last_run_at)}</span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <KButton size="sm" disabled={busy} onClick={() => handleRun(row)}>Run now</KButton>
                <KButton variant="secondary" size="sm" onClick={() => openEditModal(row)}>Edit</KButton>
                <KButton variant="ghost" size="sm" disabled={busy} onClick={() => handleToggle(row)}>{row.enabled ? 'Disable' : 'Enable'}</KButton>
              </div>
            </div>
          ))
        )}
      </div>

      {modalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, padding: 20 }}>
          <div style={{ width: '100%', maxWidth: 520, background: KColors.raised, border: `1px solid ${KColors.border}`, borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>{editing ? 'Edit payout workflow' : 'Create payout workflow'}</div>
            {formError && <div style={{ fontSize: 12, color: KColors.error, background: KColors.errorBg, borderRadius: 6, padding: '8px 10px' }}>{formError}</div>}
            <KInput label="Workflow name" value={form.name} onChange={v => setForm(prev => ({ ...prev, name: v }))} placeholder="Friday contractor payout" />
            <RecipientPicker
              value={form.recipient?.id}
              onChange={recipient => setForm(prev => applyRecipientDefaults(recipient, prev))}
              label="Recipient"
              hint="Selecting a recipient pre-fills default payout amount and schedule when configured"
            />
            <KInput label="Amount (USDC)" value={form.amount} onChange={v => setForm(prev => ({ ...prev, amount: v }))} placeholder="500" />
            <KSelect label="Schedule" value={form.schedule_cadence} onChange={v => setForm(prev => ({ ...prev, schedule_cadence: v }))} options={SCHEDULE_OPTIONS} />
            {form.schedule_cadence === 'weekly' && (
              <KSelect label="Day" value={form.schedule_day} onChange={v => setForm(prev => ({ ...prev, schedule_day: v }))} options={WEEKDAY_OPTIONS} />
            )}
            {form.schedule_cadence === 'monthly' && (
              <KInput label="Day of month (1-28)" value={form.schedule_day} onChange={v => setForm(prev => ({ ...prev, schedule_day: v }))} placeholder="1" />
            )}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <KButton variant="secondary" onClick={() => setModalOpen(false)}>Cancel</KButton>
              <KButton disabled={busy} onClick={handleSave}>{busy ? 'Saving…' : 'Save workflow'}</KButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { WorkflowsShell });
