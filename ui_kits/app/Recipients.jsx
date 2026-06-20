// Recipients — contractor payout directory (Epic 12)

const RECIPIENTS_API = `${window.KINETIC_API_BASE || ''}/recipients`;

const FALLBACK_NETWORK_OPTIONS = [
  { value: 'base', label: 'Base' },
  { value: 'ethereum', label: 'Ethereum' },
  { value: 'polygon', label: 'Polygon' },
];

async function recipientsRequest(path, options = {}) {
  const res = await fetch(`${RECIPIENTS_API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body.message || 'Recipient request failed');
    err.code = body.code;
    err.status = res.status;
    throw err;
  }
  return body;
}

function emptyForm() {
  return {
    name: '',
    wallet_address: '',
    network: 'base',
    notes: '',
    default_payout_amount: '',
    default_schedule_cadence: 'manual',
    default_schedule_day: 'friday',
  };
}

const RECIPIENT_SCHEDULE_OPTIONS = [
  { value: 'manual', label: 'Manual / per workflow' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const RECIPIENT_WEEKDAY_OPTIONS = [
  { value: 'monday', label: 'Monday' },
  { value: 'tuesday', label: 'Tuesday' },
  { value: 'wednesday', label: 'Wednesday' },
  { value: 'thursday', label: 'Thursday' },
  { value: 'friday', label: 'Friday' },
  { value: 'saturday', label: 'Saturday' },
  { value: 'sunday', label: 'Sunday' },
];

function buildRecipientPayload(form) {
  const amountRaw = String(form.default_payout_amount || '').trim();
  const amount = amountRaw ? Number(amountRaw) : null;
  return {
    name: form.name,
    wallet_address: form.wallet_address,
    network: form.network,
    notes: form.notes || null,
    default_payout_asset: amount ? 'USDC' : null,
    default_payout_amount: amount,
    default_schedule_cadence: form.default_schedule_cadence === 'manual' ? null : form.default_schedule_cadence,
    default_schedule_day: form.default_schedule_cadence === 'manual' ? null : form.default_schedule_day,
  };
}

function formatPayoutAmount(row) {
  if (row.default_payout_amount == null) return '—';
  return `${row.default_payout_amount} ${row.default_payout_asset || 'USDC'}`;
}

function Recipients({ onNavigate, onChecklistStep }) {
  const [items, setItems] = React.useState([]);
  const [search, setSearch] = React.useState('');
  const [loading, setLoading] = React.useState(true);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState('');
  const [showInactive, setShowInactive] = React.useState(false);
  const [modalOpen, setModalOpen] = React.useState(false);
  const [editing, setEditing] = React.useState(null);
  const [form, setForm] = React.useState(emptyForm());
  const [formError, setFormError] = React.useState('');
  const [confirmDeactivate, setConfirmDeactivate] = React.useState(null);
  const [networkOptions, setNetworkOptions] = React.useState(FALLBACK_NETWORK_OPTIONS);

  React.useEffect(() => {
    let cancelled = false;
    async function loadNetworks() {
      try {
        const body = await recipientsRequest('/networks');
        const items = body.items || [];
        if (!cancelled && items.length) {
          setNetworkOptions(items.map(row => ({ value: row.id, label: row.label })));
        }
      } catch {
        if (!cancelled) setNetworkOptions(FALLBACK_NETWORK_OPTIONS);
      }
    }
    loadNetworks();
    return () => { cancelled = true; };
  }, []);

  const loadRecipients = React.useCallback(async () => {
    setError('');
    try {
      const params = new URLSearchParams();
      if (search.trim()) params.set('search', search.trim());
      if (showInactive) params.set('include_inactive', 'true');
      const query = params.toString();
      const body = await recipientsRequest(query ? `?${query}` : '');
      const rows = body.items || [];
      setItems(rows);
      if (onChecklistStep && rows.some(row => row.status === 'active')) {
        onChecklistStep('recipient');
      }
      return rows;
    } catch (err) {
      setError(err.message || 'Could not load recipients.');
      return [];
    }
  }, [search, showInactive, onChecklistStep]);

  React.useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      await loadRecipients();
      if (!cancelled) setLoading(false);
    }
    boot();
    return () => { cancelled = true; };
  }, [loadRecipients]);

  React.useEffect(() => {
    if (window.lucide) lucide.createIcons();
  });

  function openCreateModal() {
    setEditing(null);
    setForm(emptyForm());
    setFormError('');
    setModalOpen(true);
  }

  function openEditModal(row) {
    setEditing(row);
    setForm({
      name: row.name || '',
      wallet_address: row.wallet_address || '',
      network: row.network || 'base',
      notes: row.notes || '',
      default_payout_amount: row.default_payout_amount != null ? String(row.default_payout_amount) : '',
      default_schedule_cadence: row.default_schedule_cadence || 'manual',
      default_schedule_day: row.default_schedule_day || 'friday',
    });
    setFormError('');
    setModalOpen(true);
  }

  async function handleSave() {
    setBusy(true);
    setFormError('');
    try {
      if (editing) {
        await recipientsRequest(`/${editing.id}`, {
          method: 'PATCH',
          body: JSON.stringify(buildRecipientPayload(form)),
        });
      } else {
        await recipientsRequest('', {
          method: 'POST',
          body: JSON.stringify(buildRecipientPayload(form)),
        });
      }
      setModalOpen(false);
      await loadRecipients();
    } catch (err) {
      setFormError(err.message || 'Could not save recipient.');
    } finally {
      setBusy(false);
    }
  }

  async function handleDeactivate(row) {
    setBusy(true);
    setError('');
    try {
      await recipientsRequest(`/${row.id}/deactivate`, { method: 'POST', body: '{}' });
      setConfirmDeactivate(null);
      await loadRecipients();
    } catch (err) {
      setError(err.message || 'Could not deactivate recipient.');
    } finally {
      setBusy(false);
    }
  }

  const activeCount = items.filter(row => row.status === 'active').length;

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16, fontSize: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Recipients</div>
          <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>
            Contractor payout destinations for your workspace · {activeCount} active
          </div>
        </div>
        <KButton onClick={openCreateModal}>Add recipient</KButton>
      </div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: '1 1 220px', maxWidth: 360 }}>
          <KInput label="Search" value={search} onChange={setSearch} placeholder="Search by name or address" />
        </div>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 12, color: KColors.fg2, cursor: 'pointer' }}>
          <input type="checkbox" checked={showInactive} onChange={e => setShowInactive(e.target.checked)} />
          Show inactive
        </label>
      </div>

      {error && (
        <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.errorBg, border: '1px solid rgba(220,38,38,0.3)', color: KColors.error, fontSize: 13 }}>
          {error}
        </div>
      )}

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.8fr 0.9fr 0.7fr 1.1fr 0.7fr 0.9fr', gap: 8, padding: '10px 14px', borderBottom: `1px solid ${KColors.border}`, fontSize: 12, fontWeight: 600, color: KColors.fg3, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          <span>Name</span><span>Payout</span><span>Frequency</span><span>Network</span><span>Wallet address</span><span>Status</span><span>Actions</span>
        </div>

        {loading ? (
          <div style={{ padding: 20, fontSize: 13, color: KColors.fg3 }}>Loading recipients…</div>
        ) : items.length === 0 ? (
          <KEmptyState
            icon="users"
            title="No contractors added"
            description="Add contractor wallet addresses so payout workflows know where to send stablecoins."
            actionLabel="Add recipient"
            onAction={openCreateModal}
          />
        ) : (
          items.map(row => (
            <div
              key={row.id}
              style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.8fr 0.9fr 0.7fr 1.1fr 0.7fr 0.9fr', gap: 8, padding: '12px 14px', borderBottom: `1px solid ${KColors.border}`, alignItems: 'center', fontSize: 14 }}
            >
              <div>
                <div style={{ color: KColors.fg1, fontWeight: 600 }}>{row.name}</div>
                {row.notes && <div style={{ marginTop: 2, fontSize: 12, color: KColors.fg3 }}>{row.notes}</div>}
              </div>
              <span style={{ color: KColors.fg1, fontFamily: 'IBM Plex Mono, monospace', fontSize: 13 }}>{formatPayoutAmount(row)}</span>
              <span style={{ color: KColors.fg2 }}>{row.default_schedule_label || '—'}</span>
              <span style={{ color: KColors.fg2 }}>{row.network_label}</span>
              <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg2 }} title={row.wallet_address}>{row.wallet_address_short}</span>
              <span><KPill status={row.status === 'active' ? 'completed' : 'pending'}>{row.status}</KPill></span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <KButton variant="secondary" size="sm" onClick={() => openEditModal(row)}>Edit</KButton>
                {row.status === 'active' && (
                  <KButton variant="danger" size="sm" disabled={busy} onClick={() => setConfirmDeactivate(row)}>Deactivate</KButton>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {modalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, padding: 20 }}>
          <div style={{ width: '100%', maxWidth: 480, background: KColors.raised, border: `1px solid ${KColors.border}`, borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>{editing ? 'Edit recipient' : 'Add recipient'}</div>
            {formError && (
              <div style={{ fontSize: 12, color: KColors.error, background: KColors.errorBg, borderRadius: 6, padding: '8px 10px' }}>{formError}</div>
            )}
            <KInput label="Name" value={form.name} onChange={v => setForm(prev => ({ ...prev, name: v }))} placeholder="Alice Chen" />
            <KSelect label="Network" value={form.network} onChange={v => setForm(prev => ({ ...prev, network: v }))} options={networkOptions} />
            <KInput label="Wallet address" value={form.wallet_address} onChange={v => setForm(prev => ({ ...prev, wallet_address: v }))} placeholder="0x..." />
            <KInput label="Notes (optional)" value={form.notes} onChange={v => setForm(prev => ({ ...prev, notes: v }))} placeholder="Contractor, monthly retainer, etc." />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <KInput label="Default payout (USDC)" value={form.default_payout_amount} onChange={v => setForm(prev => ({ ...prev, default_payout_amount: v }))} placeholder="500" />
              <KSelect label="Default frequency" value={form.default_schedule_cadence} onChange={v => setForm(prev => ({ ...prev, default_schedule_cadence: v }))} options={RECIPIENT_SCHEDULE_OPTIONS} />
            </div>
            {form.default_schedule_cadence === 'weekly' && (
              <KSelect label="Default weekday" value={form.default_schedule_day} onChange={v => setForm(prev => ({ ...prev, default_schedule_day: v }))} options={RECIPIENT_WEEKDAY_OPTIONS} />
            )}
            {form.default_schedule_cadence === 'monthly' && (
              <KInput label="Default day of month (1-28)" value={form.default_schedule_day} onChange={v => setForm(prev => ({ ...prev, default_schedule_day: v }))} placeholder="1" />
            )}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <KButton variant="secondary" onClick={() => setModalOpen(false)}>Cancel</KButton>
              <KButton disabled={busy || !form.name.trim() || !form.wallet_address.trim()} onClick={handleSave}>
                {busy ? 'Saving…' : 'Save recipient'}
              </KButton>
            </div>
          </div>
        </div>
      )}

      {confirmDeactivate && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 21, padding: 20 }}>
          <div style={{ width: '100%', maxWidth: 420, background: KColors.raised, border: `1px solid ${KColors.border}`, borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>Deactivate recipient?</div>
            <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.6 }}>
              <strong style={{ color: KColors.fg1 }}>{confirmDeactivate.name}</strong> will be hidden from payout configuration. Active workflows will warn if this destination is still linked.
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <KButton variant="secondary" onClick={() => setConfirmDeactivate(null)}>Cancel</KButton>
              <KButton variant="danger" disabled={busy} onClick={() => handleDeactivate(confirmDeactivate)}>Deactivate</KButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { Recipients });
