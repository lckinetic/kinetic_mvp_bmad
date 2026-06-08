// Dashboard — operational home

function Dashboard({ workspace, checklist, onNavigate, refreshKey = 0 }) {
  const name = workspace?.name || 'Workspace';
  const [treasuryBalance, setTreasuryBalance] = React.useState(null);
  const [treasuryLoading, setTreasuryLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    async function loadTreasury() {
      setTreasuryLoading(true);
      try {
        const res = await fetch(`${window.KINETIC_API_BASE || ''}/treasury`);
        if (res.status === 404) {
          if (!cancelled) setTreasuryBalance(null);
          return;
        }
        const body = await res.json();
        if (!cancelled && res.ok) setTreasuryBalance(body.balance);
      } catch {
        if (!cancelled) setTreasuryBalance(null);
      } finally {
        if (!cancelled) setTreasuryLoading(false);
      }
    }
    loadTreasury();
    return () => { cancelled = true; };
  }, [workspace?.id, refreshKey]);

  const balanceLabel = treasuryLoading
    ? '…'
    : treasuryBalance === null
      ? '—'
      : Number(treasuryBalance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Operations overview</div>
          <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700, color: KColors.fg1 }}>{name}</div>
          <div style={{ marginTop: 4, fontSize: 13, color: KColors.fg3 }}>Stablecoin treasury & contractor payout operations</div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('treasury')}>Fund treasury</KButton>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('recipients')}>Add recipient</KButton>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('workflows')}>Create workflow</KButton>
          <KButton variant="ghost" size="sm" onClick={() => onNavigate('activity')}>View activity</KButton>
        </div>
      </div>

      <SetupChecklist checklist={checklist} onNavigate={onNavigate} />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 12 }}>
        <KWidgetShell title="Treasury balance" actionLabel="Open treasury" onAction={() => onNavigate('treasury')}>
          <div style={{ fontSize: 28, fontWeight: 700, color: KColors.fg1 }}>{balanceLabel}</div>
          <div style={{ fontSize: 12, color: KColors.fg3 }}>
            {treasuryBalance === null && !treasuryLoading ? 'Create and fund treasury to see USDC balance' : 'USDC available for contractor payouts'}
          </div>
        </KWidgetShell>
        <KWidgetShell title="Active workflows" actionLabel="Manage" onAction={() => onNavigate('workflows')}>
          <div style={{ fontSize: 28, fontWeight: 700, color: KColors.fg1 }}>0</div>
          <div style={{ fontSize: 12, color: KColors.fg3 }}>No payout workflows configured yet</div>
        </KWidgetShell>
        <KWidgetShell title="Alerts" actionLabel="View activity" onAction={() => onNavigate('activity')}>
          <KEmptyState icon="bell" title="No issues" description="Operational alerts will appear here when monitoring is connected." />
        </KWidgetShell>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <KWidgetShell title="Recent activity" actionLabel="Activity Centre" onAction={() => onNavigate('activity')}>
          <KEmptyState icon="activity" title="No activity yet" description="Workflow runs and treasury movements will appear here." actionLabel="Go to Activity Centre" onAction={() => onNavigate('activity')} />
        </KWidgetShell>
        <KWidgetShell title="Upcoming payouts" actionLabel="Workflows" onAction={() => onNavigate('workflows')}>
          <KEmptyState icon="calendar" title="Nothing scheduled" description="Scheduled contractor payouts will show here once workflows are configured." actionLabel="Create payout workflow" onAction={() => onNavigate('workflows')} />
        </KWidgetShell>
      </div>
    </div>
  );
}

Object.assign(window, { Dashboard });
