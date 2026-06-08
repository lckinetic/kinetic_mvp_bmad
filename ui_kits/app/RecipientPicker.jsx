// Reusable recipient selector for workflow and AI flows (Epic 12)

const RECIPIENTS_API = `${window.KINETIC_API_BASE || ''}/recipients`;

function resolveRecipientValue(value) {
  if (value == null || value === '') return '';
  if (typeof value === 'object' && value.id != null) return String(value.id);
  return String(value);
}

function RecipientPicker({ value, onChange, label = 'Recipient', hint, error, disabled = false, placeholder = 'Select a recipient' }) {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState('');

  React.useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setLoadError('');
      try {
        const res = await fetch(RECIPIENTS_API);
        const body = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(body.message || 'Could not load recipients');
        if (!cancelled) setItems(body.items || []);
      } catch (err) {
        if (!cancelled) {
          setItems([]);
          setLoadError(err.message || 'Could not load recipients');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const options = [
    { value: '', label: loading ? 'Loading recipients…' : placeholder },
    ...items.map(row => ({
      value: String(row.id),
      label: `${row.name} · ${row.wallet_address_short} · ${row.network_label}`,
    })),
  ];

  function handleChange(nextValue) {
    if (!onChange) return;
    if (!nextValue) {
      onChange(null);
      return;
    }
    const selected = items.find(row => String(row.id) === String(nextValue)) || null;
    onChange(selected);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <KSelect
        label={label}
        hint={loadError || hint}
        value={resolveRecipientValue(value)}
        onChange={handleChange}
        options={options}
        disabled={disabled || loading}
      />
      {error && <span style={{ fontSize: 11, color: KColors.error }}>{error}</span>}
      {!loading && items.length === 0 && !loadError && (
        <span style={{ fontSize: 11, color: KColors.fg3 }}>Add a recipient in the Recipients screen first.</span>
      )}
    </div>
  );
}

Object.assign(window, { RecipientPicker });
