// Treasury screen — Sprint 2 (wallet, balance, funding, history)

const TREASURY_API = `${window.KINETIC_API_BASE || ''}/treasury`;

async function treasuryRequest(path, options = {}) {
  const res = await fetch(`${TREASURY_API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body.message || 'Treasury request failed');
    err.code = body.code;
    err.details = body.details;
    err.status = res.status;
    throw err;
  }
  return body;
}

function formatUsdc(amount) {
  const n = Number(amount);
  if (!Number.isFinite(n)) return '—';
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function truncateAddress(address) {
  if (!address || address.length < 12) return address || '—';
  return `${address.slice(0, 6)}…${address.slice(-4)}`;
}

function copyText(text, onDone) {
  if (!text) return;
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(() => onDone && onDone()).catch(() => {});
    return;
  }
  onDone && onDone();
}

function Treasury({ onNavigate, onChecklistStep }) {
  const [treasury, setTreasury] = React.useState(null);
  const [transfers, setTransfers] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState('');
  const [balanceError, setBalanceError] = React.useState(null);
  const [copied, setCopied] = React.useState(false);
  const [fundingCopied, setFundingCopied] = React.useState(false);
  const [demoAmount, setDemoAmount] = React.useState('1000');

  const loadTreasury = React.useCallback(async () => {
    setError('');
    try {
      const row = await treasuryRequest('');
      setTreasury(row);
      if (onChecklistStep) onChecklistStep('treasury');
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
      return row;
    } catch (err) {
      if (err.status === 404 && err.code === 'TREASURY_NOT_FOUND') {
        setTreasury(null);
        setTransfers([]);
        return null;
      }
      setError(err.message || 'Could not load treasury.');
      return null;
    }
  }, [onChecklistStep]);

  React.useEffect(() => {
    let cancelled = false;
    async function boot() {
      setLoading(true);
      await loadTreasury();
      if (!cancelled) setLoading(false);
    }
    boot();
    return () => { cancelled = true; };
  }, [loadTreasury]);

  React.useEffect(() => {
    if (window.lucide) lucide.createIcons();
  });

  async function handleCreateWallet() {
    setBusy(true);
    setError('');
    try {
      const row = await treasuryRequest('', { method: 'POST', body: JSON.stringify({}) });
      setTreasury(row);
      if (onChecklistStep) onChecklistStep('treasury');
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
    } catch (err) {
      setError(err.message || 'Could not create treasury wallet.');
    } finally {
      setBusy(false);
    }
  }

  async function handleRefresh() {
    setBusy(true);
    setBalanceError(null);
    await loadTreasury();
    setBusy(false);
  }

  async function handleSimulateDeposit() {
    const amount = Number(demoAmount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError('Enter a valid deposit amount.');
      return;
    }
    setBusy(true);
    setError('');
    setBalanceError(null);
    try {
      const res = await treasuryRequest('/transfers/simulate-deposit', {
        method: 'POST',
        body: JSON.stringify({ amount }),
      });
      setTreasury(res.treasury);
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
    } catch (err) {
      setError(err.message || 'Could not simulate deposit.');
    } finally {
      setBusy(false);
    }
  }

  async function handleBalanceProbe() {
    setBusy(true);
    setBalanceError(null);
    try {
      await treasuryRequest('/balance/check', {
        method: 'POST',
        body: JSON.stringify({ amount: 100 }),
      });
      setBalanceError(null);
    } catch (err) {
      if (err.code === 'INSUFFICIENT_BALANCE') {
        setBalanceError(err.details || { required: 100, balance: treasury?.balance ?? 0, shortfall: 100 });
      } else {
        setError(err.message || 'Balance check failed.');
      }
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 20, color: KColors.fg3, fontSize: 13 }}>Loading treasury…</div>
    );
  }

  const hasWallet = Boolean(treasury?.wallet?.address);
  const balance = treasury?.balance ?? 0;

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Treasury</div>
          <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>{treasury?.name || 'Operational stablecoin account for contractor payouts'}</div>
        </div>
        {hasWallet && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <KButton variant="secondary" size="sm" disabled={busy} onClick={handleRefresh}>Refresh balance</KButton>
            <KButton variant="ghost" size="sm" disabled={busy} onClick={handleBalanceProbe}>Check payout readiness</KButton>
          </div>
        )}
      </div>

      {error && (
        <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.errorBg, border: '1px solid rgba(220,38,38,0.3)', color: KColors.error, fontSize: 13 }}>
          {error}
        </div>
      )}

      {balanceError && (
        <div style={{ padding: '12px 14px', borderRadius: 8, background: KColors.warningBg, border: '1px solid rgba(217,119,6,0.35)', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: KColors.warning }}>Treasury balance is too low for this payout</div>
          <div style={{ fontSize: 12, color: KColors.fg2, lineHeight: 1.55 }}>
            Available {formatUsdc(balanceError.balance)} USDC · Required {formatUsdc(balanceError.required)} USDC · Shortfall {formatUsdc(balanceError.shortfall)} USDC
          </div>
          <div>
            <KButton size="sm" onClick={() => { setBalanceError(null); document.getElementById('fund-treasury-panel')?.scrollIntoView({ behavior: 'smooth' }); }}>
              Fund treasury
            </KButton>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Balance</KSectionLabel>
            <div style={{ fontSize: 32, fontWeight: 700, color: KColors.fg1 }}>{hasWallet ? `${formatUsdc(balance)} USDC` : '— USDC'}</div>
            <div style={{ marginTop: 6, fontSize: 12, color: KColors.fg3 }}>
              {hasWallet ? `${treasury.network_label || treasury.network} · ${treasury.asset}` : 'Create a treasury wallet to track balance'}
            </div>
          </div>

          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Connected wallet</KSectionLabel>
            {hasWallet ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ fontSize: 12, color: KColors.fg3 }}>{treasury.wallet.provider_label}</div>
                <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg1, wordBreak: 'break-all' }}>{treasury.wallet.address}</div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 12, color: KColors.fg3 }}>{treasury.wallet.network_label || treasury.wallet.network}</span>
                  <KButton
                    variant="secondary"
                    size="sm"
                    onClick={() => copyText(treasury.wallet.address, () => { setCopied(true); setTimeout(() => setCopied(false), 2000); })}
                  >
                    {copied ? 'Copied' : 'Copy address'}
                  </KButton>
                </div>
              </div>
            ) : (
              <KEmptyState
                icon="wallet"
                title="No treasury wallet yet"
                description="Create a treasury wallet to receive stablecoin funding and pay contractors."
                actionLabel={busy ? 'Creating…' : 'Create treasury wallet'}
                onAction={handleCreateWallet}
              />
            )}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div id="fund-treasury-panel" style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Fund treasury</KSectionLabel>
            {hasWallet ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.6 }}>
                  Send <strong style={{ color: KColors.fg1 }}>{treasury.funding.asset}</strong> on <strong style={{ color: KColors.fg1 }}>{treasury.funding.network_label}</strong> to the address below.
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', flexWrap: 'wrap' }}>
                  <div style={{ flex: '1 1 220px', padding: '10px 12px', borderRadius: 8, background: KColors.raised, border: `1px solid ${KColors.border}`, fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg1, wordBreak: 'break-all' }}>
                    {treasury.funding.address}
                  </div>
                  <KButton
                    variant="secondary"
                    size="sm"
                    onClick={() => copyText(treasury.funding.address, () => { setFundingCopied(true); setTimeout(() => setFundingCopied(false), 2000); })}
                  >
                    {fundingCopied ? 'Copied' : 'Copy funding address'}
                  </KButton>
                </div>
                <div style={{ fontSize: 12, color: KColors.warning, lineHeight: 1.5 }}>{treasury.funding.warning}</div>
                {treasury.mock_mode && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingTop: 4, borderTop: `1px dashed ${KColors.border}` }}>
                    <div style={{ fontSize: 12, color: KColors.fg3 }}>Demo mode — simulate an inbound deposit without sending funds.</div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', flexWrap: 'wrap' }}>
                      <div style={{ minWidth: 160, flex: '1 1 160px' }}>
                        <KInput label="Simulated deposit (USDC)" value={demoAmount} onChange={setDemoAmount} placeholder="1000" />
                      </div>
                      <KButton disabled={busy} onClick={handleSimulateDeposit}>Simulate deposit</KButton>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: 13, color: KColors.fg3, lineHeight: 1.6 }}>
                Deposit instructions and copy-to-clipboard funding details will appear after your treasury wallet is created.
              </div>
            )}
          </div>

          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Transaction history</KSectionLabel>
            {transfers.length === 0 ? (
              <div style={{ border: `1px dashed ${KColors.borderStrong}`, borderRadius: 8, marginTop: 8 }}>
                <KEmptyState icon="list" title="No transactions yet" description="Inbound and outbound treasury movements will be listed here." />
              </div>
            ) : (
              <div style={{ marginTop: 8, overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr style={{ color: KColors.fg3, textAlign: 'left' }}>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Date</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Type</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Amount</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Counterparty</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transfers.map(row => (
                      <tr key={row.id} style={{ borderTop: `1px solid ${KColors.border}` }}>
                        <td style={{ padding: '10px 6px', color: KColors.fg2, whiteSpace: 'nowrap' }}>{new Date(row.created_at).toLocaleString()}</td>
                        <td style={{ padding: '10px 6px', color: KColors.fg1, textTransform: 'capitalize' }}>{row.direction}</td>
                        <td style={{ padding: '10px 6px', color: KColors.fg1, fontFamily: 'IBM Plex Mono, monospace' }}>{formatUsdc(row.amount)} {row.asset}</td>
                        <td style={{ padding: '10px 6px', color: KColors.fg2 }}>{row.counterparty_label || '—'}</td>
                        <td style={{ padding: '10px 6px' }}><KPill status={row.status}>{row.status}</KPill></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Treasury });
