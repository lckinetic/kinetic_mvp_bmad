// Placeholder shells for Workflows and Activity Centre (Sprint 1)

function WorkflowsShell({ onNavigate, onChecklistStep }) {
  React.useEffect(() => {
    if (onChecklistStep) onChecklistStep('workflow');
  }, [onChecklistStep]);

  return (
    <KEmptyState
      icon="git-branch"
      title="No payout workflows configured"
      description="Create recurring contractor payout workflows from treasury to recipient wallets. Full workflow management arrives in Sprint 3."
      actionLabel="Preview treasury setup"
      onAction={() => onNavigate('treasury')}
      secondaryLabel="View legacy templates"
      onSecondary={() => onNavigate('templates')}
    />
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
