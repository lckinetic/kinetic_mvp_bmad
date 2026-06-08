// Activity Centre — unified operational timeline (Epic 14)

const ACTIVITY_API = `${window.KINETIC_API_BASE || ''}/activity`;

const FALLBACK_EVENT_TYPE_OPTIONS = [
  { value: '', label: 'All event types' },
  { value: 'payout.completed', label: 'Payout completed' },
  { value: 'payout.failed', label: 'Payout failed' },
  { value: 'treasury.deposit', label: 'Treasury funded' },
  { value: 'treasury.payout', label: 'Treasury payout sent' },
  { value: 'workflow.run_completed', label: 'Workflow run completed' },
  { value: 'workflow.run_failed', label: 'Workflow run failed' },
];

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
];

async function activityRequest(path) {
  const res = await fetch(`${ACTIVITY_API}${path}`);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.message || 'Activity request failed');
  return body;
}

function statusForPill(status) {
  if (status === 'completed') return 'completed';
  if (status === 'failed') return 'failed';
  if (status === 'running' || status === 'pending') return 'running';
  return 'pending';
}

function ActivityShell({ onNavigate }) {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [eventType, setEventType] = React.useState('');
  const [status, setStatus] = React.useState('');
  const [selected, setSelected] = React.useState(null);
  const [eventTypeOptions, setEventTypeOptions] = React.useState(FALLBACK_EVENT_TYPE_OPTIONS);

  React.useEffect(() => {
    let cancelled = false;
    async function loadEventTypes() {
      try {
        const body = await activityRequest('/event-types');
        const items = body.items || [];
        if (!cancelled && items.length) {
          setEventTypeOptions([
            { value: '', label: 'All event types' },
            ...items.map(row => ({ value: row.id, label: row.label })),
          ]);
        }
      } catch {
        if (!cancelled) setEventTypeOptions(FALLBACK_EVENT_TYPE_OPTIONS);
      }
    }
    loadEventTypes();
    return () => { cancelled = true; };
  }, []);

  const loadActivity = React.useCallback(async () => {
    setError('');
    try {
      const params = new URLSearchParams();
      if (eventType) params.set('event_type', eventType);
      if (status) params.set('status', status);
      params.set('limit', '100');
      const query = params.toString();
      const body = await activityRequest(query ? `?${query}` : '');
      setItems(body.items || []);
    } catch (err) {
      setError(err.message || 'Could not load activity feed.');
      setItems([]);
    }
  }, [eventType, status]);

  React.useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      await loadActivity();
      if (!cancelled) setLoading(false);
    }
    boot();
    return () => { cancelled = true; };
  }, [loadActivity]);

  React.useEffect(() => {
    if (window.lucide) lucide.createIcons();
  });

  async function openDetail(row) {
    try {
      const detail = await activityRequest(`/${row.id}`);
      setSelected(detail);
    } catch {
      setSelected(row);
    }
  }

  function renderNavLinks(links) {
    const nav = links?.nav || {};
    const buttons = [];
    if (nav.treasury) buttons.push({ label: 'Open treasury', route: 'treasury' });
    if (nav.workflows) buttons.push({ label: 'Open workflows', route: 'workflows' });
    if (links?.recipient_id) buttons.push({ label: 'Open recipients', route: 'recipients' });
    if (nav.activity) buttons.push({ label: 'Refresh feed', route: 'activity' });
    return buttons;
  }

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Activity Centre</div>
          <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>Unified timeline of payouts, treasury movements, and workflow runs</div>
        </div>
        <KButton variant="secondary" size="sm" onClick={() => onNavigate('runs')}>Legacy run history</KButton>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, maxWidth: 520 }}>
        <KSelect label="Event type" value={eventType} onChange={setEventType} options={eventTypeOptions} />
        <KSelect label="Status" value={status} onChange={setStatus} options={STATUS_OPTIONS} />
      </div>

      {error && (
        <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.errorBg, border: '1px solid rgba(220,38,38,0.3)', color: KColors.error, fontSize: 13 }}>{error}</div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 320px' : '1fr', gap: 12, alignItems: 'start' }}>
        <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
          {loading ? (
            <div style={{ padding: 20, fontSize: 13, color: KColors.fg3 }}>Loading activity…</div>
          ) : items.length === 0 ? (
            <KEmptyState
              icon="activity"
              title="No activity yet"
              description="Run a payout workflow or fund treasury to populate your operational timeline."
              actionLabel="Go to Workflows"
              onAction={() => onNavigate('workflows')}
              secondaryLabel="Open treasury"
              onSecondary={() => onNavigate('treasury')}
            />
          ) : (
            items.map(row => (
              <button
                key={row.id}
                type="button"
                onClick={() => openDetail(row)}
                style={{
                  display: 'grid', gridTemplateColumns: '140px 1fr auto', gap: 12, width: '100%',
                  padding: '12px 14px', borderBottom: `1px solid ${KColors.border}`, background: selected?.id === row.id ? KColors.raised : 'transparent',
                  border: 'none', borderBottomWidth: 1, borderBottomStyle: 'solid', borderBottomColor: KColors.border,
                  cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit',
                }}
              >
                <span style={{ fontSize: 12, color: KColors.fg3, whiteSpace: 'nowrap' }}>{new Date(row.created_at).toLocaleString()}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: KColors.fg1 }}>{row.title}</div>
                  <div style={{ marginTop: 4, fontSize: 12, color: KColors.fg3, lineHeight: 1.5 }}>{row.summary}</div>
                  <div style={{ marginTop: 6, fontSize: 11, color: KColors.fg3 }}>{row.event_label}</div>
                </div>
                <KPill status={statusForPill(row.status)}>{row.status}</KPill>
              </button>
            ))
          )}
        </div>

        {selected && (
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 16, display: 'flex', flexDirection: 'column', gap: 12, position: 'sticky', top: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: KColors.fg1 }}>Event detail</div>
              <KButton variant="ghost" size="sm" onClick={() => setSelected(null)}>Close</KButton>
            </div>
            <div style={{ fontSize: 12, color: KColors.fg3 }}>{new Date(selected.created_at).toLocaleString()}</div>
            <div style={{ fontSize: 15, fontWeight: 600, color: KColors.fg1 }}>{selected.title}</div>
            <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.6 }}>{selected.summary}</div>
            <KPill status={statusForPill(selected.status)}>{selected.event_label}</KPill>
            {selected.payload?.amount != null && (
              <div style={{ fontSize: 12, color: KColors.fg3 }}>Amount: {selected.payload.amount} {selected.payload.asset || 'USDC'}</div>
            )}
            {selected.links?.run_id && (
              <div style={{ fontSize: 12, color: KColors.fg3, fontFamily: 'IBM Plex Mono, monospace' }}>Run #{selected.links.run_id}</div>
            )}
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {renderNavLinks(selected.links).map(link => (
                <KButton key={link.route} variant="secondary" size="sm" onClick={() => onNavigate(link.route)}>{link.label}</KButton>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { ActivityShell });
