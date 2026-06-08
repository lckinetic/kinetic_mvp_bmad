// Settings + advanced demo links (Sprint 1)

function Settings({ workspace, onNavigate, aiCapabilities }) {
  return (
    <div style={{ padding: 20, height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 18, maxWidth: 720 }}>
      <div>
        <div style={{ fontSize: 12, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>Settings</div>
        <div style={{ marginTop: 6, fontSize: 13, color: KColors.fg3 }}>Workspace context and demo tools</div>
      </div>

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18, display: 'flex', flexDirection: 'column', gap: 10 }}>
        <KSectionLabel>Workspace</KSectionLabel>
        <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>{workspace?.name || 'No workspace'}</div>
        {workspace?.created_at && <div style={{ fontSize: 12, color: KColors.fg3 }}>Created {new Date(workspace.created_at).toLocaleString()}</div>}
      </div>

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <KSectionLabel>Environment</KSectionLabel>
        <KPill status={aiCapabilities?.mock_mode ? 'pending' : 'completed'}>
          {aiCapabilities?.mock_mode ? 'Sandbox demo mode' : 'Live AI enabled'}
        </KPill>
        <div style={{ fontSize: 12, color: KColors.fg3, lineHeight: 1.55 }}>
          Treasury, recipients, workflows, and activity run in sandbox demo mode by default. Set <code style={{ fontFamily: 'IBM Plex Mono, monospace' }}>AI_MOCK_MODE=false</code> with a valid OpenAI key for live payout draft generation.
        </div>
      </div>

      <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 18, display: 'flex', flexDirection: 'column', gap: 10 }}>
        <KSectionLabel>Advanced (demo)</KSectionLabel>
        <div style={{ fontSize: 12, color: KColors.fg3, marginBottom: 4 }}>Legacy MVP workflow tooling preserved for regression and investor demos.</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('templates')}>Legacy workflow templates</KButton>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('runs')}>Legacy operations runs</KButton>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('assistant')}>AI Assistant</KButton>
          <KButton variant="secondary" size="sm" onClick={() => onNavigate('builder')}>Workflow Builder (mock)</KButton>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Settings });
