// First-time onboarding wizard (Sprint 1)

function Onboarding({ onComplete, onGoHome }) {
  const [step, setStep] = React.useState(0);
  const [name, setName] = React.useState('');
  const [error, setError] = React.useState('');
  const [submitting, setSubmitting] = React.useState(false);

  const steps = ['Welcome', 'Audience', 'Preview', 'Workspace', 'Complete'];

  async function createWorkspace() {
    setError('');
    setSubmitting(true);
    try {
      const res = await fetch(`${window.KINETIC_API_BASE || ''}/workspaces`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim() }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(body.message || 'Could not create workspace. Check the name and try again.');
        return;
      }
      saveWorkspace({ id: body.id, name: body.name, created_at: body.created_at });
      saveChecklist(body.id, { ...DEFAULT_CHECKLIST });
      setStep(4);
    } catch {
      setError('Could not reach the server. Confirm the API is running and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{ height: '100%', overflow: 'auto', background: KColors.surface }}>
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '48px 24px 80px' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 28, flexWrap: 'wrap' }}>
          {steps.map((label, idx) => (
            <span key={label} style={{ fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 9999, background: idx === step ? KColors.primaryDim : KColors.overlay, color: idx === step ? KColors.primaryLight : KColors.fg3, border: `1px solid ${idx === step ? KColors.primary : KColors.border}` }}>
              {idx + 1}. {label}
            </span>
          ))}
        </div>

        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h1 style={{ fontSize: 34, fontWeight: 700, color: KColors.fg1, lineHeight: 1.15 }}>Programmable Financial Operations</h1>
            <p style={{ fontSize: 15, color: KColors.fg2, lineHeight: 1.65, maxWidth: 560 }}>
              Kinetic helps finance and operations teams run stablecoin treasury and contractor payout workflows without building custom integrations.
            </p>
            <div style={{ display: 'flex', gap: 10 }}>
              <KButton onClick={() => setStep(1)}>Get started</KButton>
              {onGoHome && <KButton variant="secondary" onClick={onGoHome}>Learn more</KButton>}
            </div>
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: KColors.fg1 }}>Built for operations teams</h2>
            <p style={{ fontSize: 14, color: KColors.fg2, lineHeight: 1.6 }}>Finance operations managers, treasury leads, and startup operators use Kinetic to fund treasury, manage recipients, and run payout workflows from one control centre.</p>
            <KButton onClick={() => setStep(2)}>Continue</KButton>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: KColors.fg1 }}>What happens next</h2>
            <div style={{ display: 'grid', gap: 10 }}>
              {['Set up treasury', 'Add contractor recipients', 'Configure payout workflows', 'Monitor activity'].map((item, idx) => (
                <div key={item} style={{ display: 'flex', gap: 10, alignItems: 'center', padding: '10px 12px', background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 8 }}>
                  <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: KColors.primaryLight }}>{idx + 1}</span>
                  <span style={{ fontSize: 13, color: KColors.fg1 }}>{item}</span>
                </div>
              ))}
            </div>
            <KButton onClick={() => setStep(3)}>Continue</KButton>
          </div>
        )}

        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 420 }}>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: KColors.fg1 }}>Create your workspace</h2>
            <p style={{ fontSize: 14, color: KColors.fg2, lineHeight: 1.6 }}>A workspace groups your treasury, recipients, workflows, and activity history.</p>
            <KInput label="Workspace name" value={name} onChange={setName} placeholder="Acme Treasury Ops" error={error} />
            <div style={{ display: 'flex', gap: 10 }}>
              <KButton disabled={submitting || !name.trim()} onClick={createWorkspace}>{submitting ? 'Creating…' : 'Create workspace'}</KButton>
              <KButton variant="secondary" onClick={() => setStep(2)}>Back</KButton>
            </div>
          </div>
        )}

        {step === 4 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: KColors.fg1 }}>Workspace ready</h2>
            <p style={{ fontSize: 14, color: KColors.fg2, lineHeight: 1.6 }}>Your dashboard includes a setup checklist to guide treasury funding, recipients, and your first payout workflow.</p>
            <KButton onClick={onComplete}>Go to Dashboard</KButton>
          </div>
        )}
      </div>
    </div>
  );
}

Object.assign(window, { Onboarding });
