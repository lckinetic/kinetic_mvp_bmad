// Treasury screen — Sprint 2 (wallet, balance, funding, history)

const TREASURY_API = `${window.KINETIC_API_BASE || ''}/treasury`;

const WALLET_SOURCE_OPTIONS = [
  { id: 'privy', label: 'Privy custodial wallet', description: 'Recommended for MVP demos and production treasury operations.', active: true },
  { id: 'metamask', label: 'MetaMask', description: 'UI preview only — live wallet connect coming soon.', active: false },
  { id: 'trust', label: 'Trust Wallet', description: 'UI preview only — live wallet connect coming soon.', active: false },
];

const FIAT_TREASURY_ACCOUNTS = [
  { id: 'corp-usd', label: 'Corporate USD operating', currency: 'USD', balance: 250000 },
  { id: 'corp-gbp', label: 'Corporate GBP operating', currency: 'GBP', balance: 180000 },
];

const ONRAMP_PARTNERS = [
  { id: 'banxa', label: 'Banxa sandbox on-ramp' },
];

const FUNDING_STEPS = ['Fiat source', 'On-ramp', 'Treasury deposit'];

function FundingStepHeader({ step, current, label, status }) {
  const isActive = current === step;
  const isDone = current > step || status === 'completed';
  const color = isDone ? KColors.success : isActive ? KColors.primaryLight : KColors.fg3;
  const bg = isDone ? KColors.successBg : isActive ? KColors.primaryDim : KColors.overlay;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: '1 1 120px' }}>
      <div style={{
        width: 28, height: 28, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: bg, border: `1px solid ${isActive ? KColors.primary : KColors.borderStrong}`, color, fontSize: 12, fontWeight: 700,
      }}>
        {isDone ? '✓' : step}
      </div>
      <div style={{ fontSize: 13, fontWeight: isActive ? 600 : 500, color: isActive ? KColors.fg1 : KColors.fg3 }}>{label}</div>
    </div>
  );
}

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

function Treasury({ onNavigate, onChecklistStep }) {
  const [treasury, setTreasury] = React.useState(null);
  const [transfers, setTransfers] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [busy, setBusy] = React.useState(false);
  const [refreshing, setRefreshing] = React.useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = React.useState(null);
  const [walletSource, setWalletSource] = React.useState('privy');
  const [error, setError] = React.useState('');
  const [balanceError, setBalanceError] = React.useState(null);
  const [fundingStep, setFundingStep] = React.useState(1);
  const [fiatAccountId, setFiatAccountId] = React.useState(FIAT_TREASURY_ACCOUNTS[0].id);
  const [fiatAmount, setFiatAmount] = React.useState('1000');
  const [onrampPartner, setOnrampPartner] = React.useState(ONRAMP_PARTNERS[0].id);
  const [onrampQuote, setOnrampQuote] = React.useState(null);
  const [fundingBusy, setFundingBusy] = React.useState(false);
  const [fundingSuccess, setFundingSuccess] = React.useState(null);

  const loadTreasury = React.useCallback(async () => {
    setError('');
    try {
      const row = await treasuryRequest('');
      setTreasury(row);
      if (onChecklistStep) onChecklistStep('treasury');
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
      setLastRefreshedAt(new Date());
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
    if (walletSource !== 'privy') {
      setError('Live MetaMask and Trust Wallet connections are coming soon. Use Privy custodial wallet for the MVP demo.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const row = await treasuryRequest('', { method: 'POST', body: JSON.stringify({}) });
      setTreasury(row);
      if (onChecklistStep) onChecklistStep('treasury');
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
      setLastRefreshedAt(new Date());
    } catch (err) {
      setError(err.message || 'Could not create treasury wallet.');
    } finally {
      setBusy(false);
    }
  }

  async function handleRefresh() {
    setRefreshing(true);
    setBalanceError(null);
    await loadTreasury();
    setRefreshing(false);
  }

  async function handleSimulateDeposit(amount, counterpartyLabel) {
    if (!Number.isFinite(amount) || amount <= 0) {
      setError('Enter a valid deposit amount.');
      return null;
    }
    setBusy(true);
    setFundingBusy(true);
    setError('');
    setBalanceError(null);
    try {
      const res = await treasuryRequest('/transfers/simulate-deposit', {
        method: 'POST',
        body: JSON.stringify({
          amount,
          counterparty_label: counterpartyLabel,
        }),
      });
      setTreasury(res.treasury);
      const history = await treasuryRequest('/transfers');
      setTransfers(history.items || []);
      setLastRefreshedAt(new Date());
      return res;
    } catch (err) {
      setError(err.message || 'Could not complete treasury deposit.');
      return null;
    } finally {
      setBusy(false);
      setFundingBusy(false);
    }
  }

  function resetFundingFlow() {
    setFundingStep(1);
    setOnrampQuote(null);
    setFundingSuccess(null);
  }

  async function handleLinkFiatSource() {
    setFundingBusy(true);
    setError('');
    await new Promise(resolve => setTimeout(resolve, 500));
    setFundingStep(2);
    setFundingBusy(false);
  }

  async function handleSimulateOnramp() {
    const amount = Number(fiatAmount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError('Enter a valid fiat amount to on-ramp.');
      return;
    }
    const account = FIAT_TREASURY_ACCOUNTS.find(row => row.id === fiatAccountId) || FIAT_TREASURY_ACCOUNTS[0];
    setFundingBusy(true);
    setError('');
    await new Promise(resolve => setTimeout(resolve, 700));
    setOnrampQuote({
      fiat_amount: amount,
      fiat_currency: account.currency,
      usdc_amount: amount,
      partner: ONRAMP_PARTNERS.find(row => row.id === onrampPartner)?.label || 'Banxa sandbox on-ramp',
      reference: `SIM-ONRAMP-${Date.now().toString(36).slice(-6).toUpperCase()}`,
    });
    setFundingStep(3);
    setFundingBusy(false);
  }

  async function handleCompleteFunding() {
    if (!onrampQuote) return;
    const res = await handleSimulateDeposit(
      onrampQuote.usdc_amount,
      'Privy treasury · simulated on-ramp deposit',
    );
    if (res) {
      setFundingSuccess({
        amount: onrampQuote.usdc_amount,
        reference: onrampQuote.reference,
      });
      setFundingStep(1);
      setOnrampQuote(null);
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
      <div style={{ padding: 20, color: KColors.fg3, fontSize: 14 }}>Loading treasury…</div>
    );
  }

  const hasWallet = Boolean(treasury?.wallet?.address);
  const balance = treasury?.balance ?? 0;
  const selectedSource = WALLET_SOURCE_OPTIONS.find(option => option.id === walletSource) || WALLET_SOURCE_OPTIONS[0];

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16, fontSize: 14 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 13, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Treasury</div>
          <div style={{ marginTop: 6, fontSize: 14, color: KColors.fg3 }}>{treasury?.name || 'Operational stablecoin account for contractor payouts'}</div>
        </div>
        {hasWallet && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <KButton variant="secondary" size="sm" disabled={busy || refreshing} onClick={handleRefresh}>
              {refreshing ? 'Refreshing…' : 'Refresh balance'}
            </KButton>
            <KButton variant="ghost" size="sm" disabled={busy || refreshing} onClick={handleBalanceProbe}>Check payout readiness</KButton>
            {lastRefreshedAt && !refreshing && (
              <span style={{ fontSize: 12, color: KColors.fg3 }}>Updated {lastRefreshedAt.toLocaleTimeString()}</span>
            )}
          </div>
        )}
      </div>

      {error && (
        <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.errorBg, border: '1px solid rgba(220,38,38,0.3)', color: KColors.error, fontSize: 14 }}>
          {error}
        </div>
      )}

      {balanceError && (
        <div style={{ padding: '12px 14px', borderRadius: 8, background: KColors.warningBg, border: '1px solid rgba(217,119,6,0.35)', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: KColors.warning }}>Treasury balance is too low for this payout</div>
          <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.55 }}>
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
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18, transition: refreshing ? 'opacity 0.6' : 'opacity 1' }}>
            <KSectionLabel>Balance</KSectionLabel>
            <div style={{ fontSize: 34, fontWeight: 700, color: KColors.fg1 }}>{hasWallet ? `${formatUsdc(balance)} USDC` : '— USDC'}</div>
            <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>
              {hasWallet ? `${treasury.network_label || treasury.network} · ${treasury.asset}` : 'Create a Privy treasury wallet to track balance'}
            </div>
          </div>

          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Treasury wallet</KSectionLabel>
            {hasWallet ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                  <KPill status="completed">{treasury.wallet.provider_label || 'Privy custodial wallet'}</KPill>
                  <span style={{ fontSize: 12, color: KColors.fg3 }}>More custodial providers coming soon</span>
                </div>
                <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 13, color: KColors.fg1, wordBreak: 'break-all' }}>{treasury.wallet.address}</div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 13, color: KColors.fg3 }}>{treasury.wallet.network_label || treasury.wallet.network}</span>
                  <KCopyIconButton text={treasury.wallet.address} title="Copy wallet address" />
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.6 }}>
                  Choose how your operational treasury wallet will be provisioned. MVP demos use a <strong style={{ color: KColors.fg1 }}>Privy custodial wallet</strong>.
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {WALLET_SOURCE_OPTIONS.map(option => (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => setWalletSource(option.id)}
                      style={{
                        textAlign: 'left',
                        padding: '10px 12px',
                        borderRadius: 8,
                        border: `1px solid ${walletSource === option.id ? KColors.primary : KColors.borderStrong}`,
                        background: walletSource === option.id ? KColors.primaryDim : KColors.raised,
                        color: KColors.fg1,
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 14, fontWeight: 600 }}>{option.label}</span>
                        {!option.active && <KPill status="pending">Preview</KPill>}
                        {option.active && <KPill status="completed">Active</KPill>}
                      </div>
                      <div style={{ marginTop: 4, fontSize: 12, color: KColors.fg3, lineHeight: 1.5 }}>{option.description}</div>
                    </button>
                  ))}
                </div>
                <KButton disabled={busy} onClick={handleCreateWallet}>
                  {busy ? 'Creating…' : `Create ${selectedSource.label}`}
                </KButton>
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div id="fund-treasury-panel" style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Fund treasury</KSectionLabel>
            {hasWallet ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {fundingSuccess && (
                  <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.successBg, border: '1px solid rgba(74,222,128,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
                    <div style={{ fontSize: 14, color: KColors.success }}>
                      Treasury funded with {formatUsdc(fundingSuccess.amount)} USDC
                      {fundingSuccess.reference ? ` · ${fundingSuccess.reference}` : ''}
                    </div>
                    <KButton size="sm" variant="secondary" onClick={() => setFundingSuccess(null)}>Dismiss</KButton>
                  </div>
                )}

                {treasury.mock_mode ? (
                  <>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', padding: '4px 0 8px' }}>
                      {FUNDING_STEPS.map((label, idx) => (
                        <FundingStepHeader key={label} step={idx + 1} current={fundingStep} label={label} />
                      ))}
                    </div>

                    {fundingStep === 1 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 14, borderRadius: 8, background: KColors.raised, border: `1px solid ${KColors.border}` }}>
                        <KSelect
                          label="Corporate fiat treasury account"
                          value={fiatAccountId}
                          onChange={setFiatAccountId}
                          options={FIAT_TREASURY_ACCOUNTS.map(row => ({
                            value: row.id,
                            label: `${row.label} · ${row.currency} ${row.balance.toLocaleString()}`,
                          }))}
                        />
                        <KButton disabled={fundingBusy} onClick={handleLinkFiatSource}>
                          {fundingBusy ? 'Linking…' : 'Link fiat treasury'}
                        </KButton>
                      </div>
                    )}

                    {fundingStep === 2 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 14, borderRadius: 8, background: KColors.raised, border: `1px solid ${KColors.border}` }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                          <KInput label="Fiat amount" value={fiatAmount} onChange={setFiatAmount} placeholder="1000" />
                          <KSelect
                            label="On-ramp partner"
                            value={onrampPartner}
                            onChange={setOnrampPartner}
                            options={ONRAMP_PARTNERS.map(row => ({ value: row.id, label: row.label }))}
                          />
                        </div>
                        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                          <KButton disabled={fundingBusy} onClick={handleSimulateOnramp}>
                            {fundingBusy ? 'Converting…' : 'Simulate on-ramp to USDC'}
                          </KButton>
                          <KButton variant="secondary" disabled={fundingBusy} onClick={() => setFundingStep(1)}>Back</KButton>
                        </div>
                      </div>
                    )}

                    {fundingStep === 3 && onrampQuote && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 14, borderRadius: 8, background: KColors.raised, border: `1px solid ${KColors.border}` }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
                          <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.overlay, border: `1px solid ${KColors.border}` }}>
                            <div style={{ fontSize: 12, color: KColors.fg3 }}>On-ramp quote</div>
                            <div style={{ marginTop: 4, fontSize: 15, fontWeight: 600, color: KColors.fg1 }}>
                              {formatUsdc(onrampQuote.fiat_amount)} {onrampQuote.fiat_currency} → {formatUsdc(onrampQuote.usdc_amount)} USDC
                            </div>
                          </div>
                          <div style={{ padding: '10px 12px', borderRadius: 8, background: KColors.overlay, border: `1px solid ${KColors.border}` }}>
                            <div style={{ fontSize: 12, color: KColors.fg3 }}>Partner reference</div>
                            <div style={{ marginTop: 4, fontFamily: 'IBM Plex Mono, monospace', fontSize: 13, color: KColors.fg1 }}>{onrampQuote.reference}</div>
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: 12, color: KColors.fg3, marginBottom: 6 }}>Destination · Privy treasury wallet</div>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                            <div style={{ flex: '1 1 220px', padding: '10px 12px', borderRadius: 8, background: KColors.sunken, border: `1px solid ${KColors.border}`, fontFamily: 'IBM Plex Mono, monospace', fontSize: 13, color: KColors.fg1, wordBreak: 'break-all' }}>
                              {treasury.funding.address}
                            </div>
                            <KCopyIconButton text={treasury.funding.address} title="Copy funding address" />
                          </div>
                        </div>
                        <div style={{ fontSize: 12, color: KColors.warning }}>{treasury.funding.warning}</div>
                        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                          <KButton disabled={fundingBusy} onClick={handleCompleteFunding}>
                            {fundingBusy ? 'Depositing…' : `Deposit ${formatUsdc(onrampQuote.usdc_amount)} USDC`}
                          </KButton>
                          <KButton variant="secondary" disabled={fundingBusy} onClick={() => { setFundingStep(2); setOnrampQuote(null); }}>Back</KButton>
                        </div>
                      </div>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <KButton variant="ghost" size="sm" onClick={resetFundingFlow}>Restart funding flow</KButton>
                    </div>
                  </>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <div style={{ fontSize: 13, color: KColors.fg3 }}>Send USDC on {treasury.funding.network_label} to your Privy treasury wallet.</div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                      <div style={{ flex: '1 1 220px', padding: '10px 12px', borderRadius: 8, background: KColors.raised, border: `1px solid ${KColors.border}`, fontFamily: 'IBM Plex Mono, monospace', fontSize: 13, color: KColors.fg1, wordBreak: 'break-all' }}>
                        {treasury.funding.address}
                      </div>
                      <KCopyIconButton text={treasury.funding.address} title="Copy funding address" />
                    </div>
                    <div style={{ fontSize: 12, color: KColors.warning }}>{treasury.funding.warning}</div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: 14, color: KColors.fg3, lineHeight: 1.6 }}>
                Create a Privy treasury wallet to start the funding flow.
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
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                  <thead>
                    <tr style={{ color: KColors.fg3, textAlign: 'left' }}>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Date</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Type</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Amount</th>
                      <th style={{ padding: '8px 6px', fontWeight: 600 }}>Source</th>
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
