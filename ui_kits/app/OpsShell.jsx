// Placeholder shells for Workflows and Activity Centre

function WorkflowsShell({ onNavigate, onChecklistStep }) {
  const [recipient, setRecipient] = React.useState(null);
  const [amount, setAmount] = React.useState('500');

  React.useEffect(() => {
    if (onChecklistStep) onChecklistStep('workflow');
  }, [onChecklistStep]);

  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Workflows</div>
        <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>
          Configure recurring contractor payout workflows from treasury to recipient wallets.
        </div>
      </div>

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18, display: 'flex', flexDirection: 'column', gap: 14, maxWidth: 520 }}>
        <KSectionLabel>Contractor payout preview</KSectionLabel>
        <div style={{ fontSize: 13, color: KColors.fg2, lineHeight: 1.6 }}>
          Full workflow create/edit/run arrives in Epic 13. Use this preview to validate recipient selection from your directory.
        </div>
        <RecipientPicker
          value={recipient}
          onChange={setRecipient}
          label="Recipient"
          hint="Select an active contractor payout destination"
        />
        <KInput label="Amount (USDC)" value={amount} onChange={setAmount} placeholder="500" />
        {recipient && (
          <div style={{ fontSize: 12, color: KColors.fg3, lineHeight: 1.5 }}>
            Draft destination: {recipient.name} · {recipient.wallet_address_short} · {recipient.network_label}
          </div>
        )}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('recipients')}>Manage recipients</KButton>
          <KButton variant="ghost" size="sm" onClick={() => onNavigate('treasury')}>Open treasury</KButton>
        </div>
      </div>

      <KEmptyState
        icon="git-branch"
        title="No payout workflows configured"
        description="Saved payout workflows with schedules and manual run controls will appear here once Epic 13 workflow management is live."
        actionLabel="View legacy templates"
        onAction={() => onNavigate('templates')}
      />
    </div>
  );
}

function ActivityShell({ onNavigate }) {
  return (
    <KEmptyState
      icon="activity"
      title="No activity yet"
      description="Workflow runs, treasury movements, and alerts will appear in your Activity Centre once operations begin."
      actionLabel="Go to Dashboard"
      onAction={() => onNavigate('dashboard')}
      secondaryLabel="Legacy run history"
      onSecondary={() => onNavigate('runs')}
    />
  );
}

Object.assign(window, { WorkflowsShell, ActivityShell });
