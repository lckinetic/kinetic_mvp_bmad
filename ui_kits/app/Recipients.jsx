// Recipients screen shell (Sprint 1)

function Recipients({ onNavigate, onChecklistStep }) {
  const [showStub, setShowStub] = React.useState(false);

  React.useEffect(() => {
    if (onChecklistStep) onChecklistStep('recipient');
  }, [onChecklistStep]);
  const [name, setName] = React.useState('');
  const [address, setAddress] = React.useState('');
  const [network, setNetwork] = React.useState('base');

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Recipients</div>
          <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>Contractor payout destinations for your workspace</div>
        </div>
        <KButton onClick={() => setShowStub(true)}>Add recipient</KButton>
      </div>

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr 1.4fr 0.6fr', gap: 8, padding: '10px 14px', borderBottom: `1px solid ${KColors.border}`, fontSize: 11, fontWeight: 600, color: KColors.fg3, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          <span>Name</span><span>Network</span><span>Wallet address</span><span>Status</span>
        </div>
        <KEmptyState
          icon="users"
          title="No contractors added"
          description="Add contractor wallet addresses so payout workflows know where to send stablecoins."
          actionLabel="Add recipient"
          onAction={() => setShowStub(true)}
        />
      </div>

      {showStub && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, padding: 20 }}>
          <div style={{ width: '100%', maxWidth: 460, background: KColors.raised, border: `1px solid ${KColors.border}`, borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>Add recipient</div>
            <div style={{ fontSize: 12, color: KColors.warning, background: KColors.warningBg, borderRadius: 6, padding: '8px 10px' }}>
              Recipient saving connects in Sprint 2. This form preview shows the planned fields.
            </div>
            <KInput label="Name" value={name} onChange={setName} placeholder="Alice Chen" />
            <KSelect label="Network" value={network} onChange={setNetwork} options={[
              { value: 'base', label: 'Base' },
              { value: 'ethereum', label: 'Ethereum' },
              { value: 'polygon', label: 'Polygon' },
            ]} />
            <KInput label="Wallet address" value={address} onChange={setAddress} placeholder="0x..." />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
              <KButton variant="secondary" onClick={() => setShowStub(false)}>Close</KButton>
              <KButton disabled>Save recipient</KButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { Recipients });
