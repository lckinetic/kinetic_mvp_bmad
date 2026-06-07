// Treasury screen shell (Sprint 1)

function Treasury({ onNavigate, onChecklistStep }) {
  React.useEffect(() => {
    if (onChecklistStep) onChecklistStep('treasury');
  }, [onChecklistStep]);

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Treasury</div>
        <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>Operational stablecoin account for contractor payouts</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Balance</KSectionLabel>
            <div style={{ fontSize: 32, fontWeight: 700, color: KColors.fg1 }}>— USDC</div>
            <div style={{ marginTop: 6, fontSize: 12, color: KColors.fg3 }}>Live balance connects in Sprint 2</div>
          </div>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Connected wallet</KSectionLabel>
            <KEmptyState
              icon="wallet"
              title="No treasury wallet yet"
              description="Create a treasury wallet to receive stablecoin funding and pay contractors."
              actionLabel="Create treasury wallet"
              onAction={() => {}}
              secondaryLabel="Available in Sprint 2"
            />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Fund treasury</KSectionLabel>
            <div style={{ fontSize: 13, color: KColors.fg3, lineHeight: 1.6 }}>
              Deposit instructions and copy-to-clipboard funding details will appear here after your treasury wallet is created.
            </div>
          </div>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18 }}>
            <KSectionLabel>Transaction history</KSectionLabel>
            <div style={{ border: `1px dashed ${KColors.borderStrong}`, borderRadius: 8, marginTop: 8 }}>
              <KEmptyState icon="list" title="No transactions yet" description="Inbound and outbound treasury movements will be listed here." />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Treasury });
