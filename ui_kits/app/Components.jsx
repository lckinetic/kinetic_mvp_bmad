// Kinetic UI Kit — Shared Components
// Exported to window for use across files

const KColors = {
  surface: '#0d0e11',
  raised: '#13151a',
  overlay: '#1a1d24',
  sunken: '#0a0b0e',
  border: '#1e2028',
  borderStrong: '#2a2d38',
  fg1: '#f0f2f5',
  fg2: '#9399a8',
  fg3: '#636878',
  primary: '#5b5ff5',
  primaryLight: '#8183f8',
  primaryDim: 'rgba(91,95,245,0.15)',
  success: '#4ade80',
  successBg: 'rgba(22,163,74,0.12)',
  error: '#f87171',
  errorBg: 'rgba(220,38,38,0.12)',
  warning: '#fbbf24',
  warningBg: 'rgba(217,119,6,0.12)',
};

// ── Logo ──────────────────────────────────────────────
function KLogo({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <rect width="40" height="40" rx="8" fill={KColors.raised}/>
      <rect x="10" y="8" width="3" height="24" fill={KColors.primary} rx="1.5"/>
      <line x1="13" y1="20" x2="28" y2="8" stroke={KColors.primary} strokeWidth="3" strokeLinecap="round"/>
      <line x1="13" y1="20" x2="28" y2="32" stroke={KColors.primary} strokeWidth="3" strokeLinecap="round"/>
    </svg>
  );
}

// ── Button ────────────────────────────────────────────
function KButton({ children, variant = 'primary', size = 'md', disabled, onClick, style }) {
  const base = {
    fontFamily: 'inherit', fontWeight: 500, cursor: disabled ? 'not-allowed' : 'pointer',
    border: 'none', borderRadius: 6, transition: 'opacity 120ms ease-out, transform 120ms ease-out',
    display: 'inline-flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap',
    opacity: disabled ? 0.4 : 1,
  };
  const sizes = { sm: { fontSize: 12, padding: '5px 12px' }, md: { fontSize: 14, padding: '9px 18px' } };
  const variants = {
    primary: { background: KColors.primary, color: '#fff' },
    secondary: { background: KColors.overlay, color: KColors.fg1, border: `1px solid ${KColors.borderStrong}` },
    ghost: { background: 'transparent', color: KColors.primaryLight, border: `1px solid ${KColors.primary}` },
    danger: { background: KColors.errorBg, color: KColors.error, border: `1px solid rgba(220,38,38,0.3)` },
  };
  const [hovered, setHovered] = React.useState(false);
  const [pressed, setPressed] = React.useState(false);
  return (
    <button
      type="button"
      style={{ ...base, ...sizes[size], ...variants[variant], ...(hovered && !disabled ? { opacity: 0.85 } : {}), ...(pressed && !disabled ? { transform: 'scale(0.98)' } : {}), ...style }}
      disabled={disabled}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => { setHovered(false); setPressed(false); }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
    >{children}</button>
  );
}

// ── Input ─────────────────────────────────────────────
function KInput({ label, hint, error, type = 'text', value, onChange, placeholder, min, max, step }) {
  const [focused, setFocused] = React.useState(false);
  const inputId = React.useId();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {label && <label htmlFor={inputId} style={{ fontSize: 12, fontWeight: 500, color: KColors.fg2, letterSpacing: '0.01em' }}>{label}</label>}
      <input
        id={inputId}
        type={type} value={value} onChange={e => onChange && onChange(e.target.value)}
        placeholder={placeholder} min={min} max={max} step={step}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        style={{
          fontFamily: 'inherit', fontSize: 14, padding: '8px 12px',
          background: KColors.sunken, color: KColors.fg1,
          border: `1px solid ${error ? KColors.error : focused ? KColors.primary : KColors.borderStrong}`,
          borderRadius: 4, outline: 'none', width: '100%', boxSizing: 'border-box',
          transition: 'border-color 120ms ease-out',
        }}
      />
      {hint && !error && <span style={{ fontSize: 11, color: KColors.fg3 }}>{hint}</span>}
      {error && <span style={{ fontSize: 11, color: KColors.error }}>{error}</span>}
    </div>
  );
}

// ── Select ────────────────────────────────────────────
function KSelect({ label, hint, options, value, onChange, disabled = false }) {
  const [focused, setFocused] = React.useState(false);
  const selectId = React.useId();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {label && <label htmlFor={selectId} style={{ fontSize: 12, fontWeight: 500, color: KColors.fg2, letterSpacing: '0.01em' }}>{label}</label>}
      <select
        id={selectId}
        value={value} onChange={e => onChange && onChange(e.target.value)}
        onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
        disabled={disabled}
        style={{
          fontFamily: 'inherit', fontSize: 14, padding: '8px 12px',
          background: KColors.sunken, color: KColors.fg1,
          border: `1px solid ${focused ? KColors.primary : KColors.borderStrong}`,
          borderRadius: 4, outline: 'none', width: '100%', boxSizing: 'border-box',
          cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.55 : 1,
        }}
      >
        {options.map(o => <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>)}
      </select>
      {hint && <span style={{ fontSize: 11, color: KColors.fg3 }}>{hint}</span>}
    </div>
  );
}

// ── Pill / Badge ──────────────────────────────────────
function KPill({ status, children }) {
  const styles = {
    completed: { bg: KColors.successBg, color: KColors.success, dot: KColors.success },
    running:   { bg: KColors.warningBg, color: KColors.warning, dot: KColors.warning },
    failed:    { bg: KColors.errorBg,   color: KColors.error,   dot: KColors.error },
    pending:   { bg: KColors.overlay,   color: KColors.fg3,     dot: KColors.fg3 },
    default:   { bg: KColors.overlay,   color: KColors.fg2,     dot: KColors.fg3 },
  };
  const s = styles[status] || styles.default;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 9px', borderRadius: 9999, background: s.bg, color: s.color, fontSize: 11, fontWeight: 500, whiteSpace: 'nowrap' }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: s.dot, flexShrink: 0 }}/>
      {children ?? status}
    </span>
  );
}

// ── Stepper ───────────────────────────────────────────
function KStepper({ steps, statuses }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0 }}>
      {steps.map((step, i) => {
        const st = statuses[step] || 'pending';
        const colors = {
          completed: { bg: KColors.successBg, border: 'rgba(74,222,128,0.2)', color: KColors.success },
          running:   { bg: KColors.warningBg, border: 'rgba(251,191,36,0.2)', color: KColors.warning },
          failed:    { bg: KColors.errorBg,   border: 'rgba(248,113,113,0.2)', color: KColors.error },
          pending:   { bg: KColors.overlay,   border: KColors.borderStrong,   color: KColors.fg3 },
        };
        const c = colors[st] || colors.pending;
        return (
          <React.Fragment key={step}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '5px 11px', borderRadius: 9999, background: c.bg, border: `1px solid ${c.border}`, color: c.color, fontSize: 12, fontWeight: 500, whiteSpace: 'nowrap' }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: c.color, opacity: 0.8 }}/>
              {step}
            </div>
            {i < steps.length - 1 && <div style={{ width: 18, height: 1, background: KColors.border, flexShrink: 0 }}/>}
          </React.Fragment>
        );
      })}
    </div>
  );
}

// ── Steps Table ───────────────────────────────────────
function KStepsTable({ steps }) {
  if (!steps || !steps.length) return <div style={{ fontSize: 13, color: KColors.fg3 }}>No steps yet.</div>;
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          {['#','Step','Status','Duration'].map(h => (
            <th key={h} style={{ fontSize: 11, fontWeight: 600, color: KColors.fg3, textAlign: 'left', padding: '6px 10px', borderBottom: `1px solid ${KColors.border}`, letterSpacing: '0.04em', textTransform: 'uppercase' }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {steps.map((s, i) => (
          <tr key={i} style={{ borderBottom: `1px solid ${KColors.border}` }}>
            <td style={{ padding: '9px 10px', fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>{s.seq ?? i+1}</td>
            <td style={{ padding: '9px 10px', fontSize: 13, color: KColors.fg1 }}>{s.step_name}</td>
            <td style={{ padding: '9px 10px' }}><KPill status={s.status}/></td>
            <td style={{ padding: '9px 10px', fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, color: KColors.fg3 }}>{s.duration_ms != null ? `${s.duration_ms} ms` : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Code Block ────────────────────────────────────────
function KCodeBlock({ value, onChange, readOnly, minHeight = 120 }) {
  return (
    <textarea
      value={value}
      onChange={e => onChange && onChange(e.target.value)}
      readOnly={readOnly}
      spellCheck={false}
      style={{
        fontFamily: 'IBM Plex Mono, monospace', fontSize: 12, lineHeight: 1.6,
        width: '100%', minHeight, padding: 12, boxSizing: 'border-box',
        background: KColors.sunken, color: KColors.fg1,
        border: `1px solid ${KColors.border}`, borderRadius: 6,
        resize: 'vertical', outline: 'none',
      }}
    />
  );
}

// ── Section label ─────────────────────────────────────
function KSectionLabel({ children }) {
  return <div style={{ fontSize: 11, fontWeight: 600, color: KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8 }}>{children}</div>;
}

// ── Divider ───────────────────────────────────────────
function KDivider() {
  return <div style={{ height: 1, background: KColors.border, margin: '16px 0' }}/>;
}

// ── Workspace client storage (Sprint 1) ─────────────
const WORKSPACE_STORAGE_KEY = 'kinetic_workspace';
const CHECKLIST_STORAGE_PREFIX = 'kinetic_checklist_';

const DEFAULT_CHECKLIST = {
  treasury: false,
  recipient: false,
  workflow: false,
  firstRun: false,
};

function loadWorkspace() {
  try {
    const raw = window.localStorage.getItem(WORKSPACE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed.id !== 'number' || !parsed.name) return null;
    return parsed;
  } catch {
    return null;
  }
}

function saveWorkspace(workspace) {
  window.localStorage.setItem(WORKSPACE_STORAGE_KEY, JSON.stringify(workspace));
}

function clearWorkspace() {
  window.localStorage.removeItem(WORKSPACE_STORAGE_KEY);
}

function loadChecklist(workspaceId) {
  if (!workspaceId) return { ...DEFAULT_CHECKLIST };
  try {
    const raw = window.localStorage.getItem(`${CHECKLIST_STORAGE_PREFIX}${workspaceId}`);
    if (!raw) return { ...DEFAULT_CHECKLIST };
    return { ...DEFAULT_CHECKLIST, ...JSON.parse(raw) };
  } catch {
    return { ...DEFAULT_CHECKLIST };
  }
}

function saveChecklist(workspaceId, checklist) {
  if (!workspaceId) return;
  window.localStorage.setItem(`${CHECKLIST_STORAGE_PREFIX}${workspaceId}`, JSON.stringify(checklist));
}

function markChecklistStep(workspaceId, step, value = true) {
  const next = { ...loadChecklist(workspaceId), [step]: value };
  saveChecklist(workspaceId, next);
  return next;
}

// ── Empty state ───────────────────────────────────────
function KEmptyState({ icon = 'inbox', title, description, actionLabel, onAction, secondaryLabel, onSecondary }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '48px 24px', gap: 12, minHeight: 240 }}>
      <div style={{ width: 48, height: 48, borderRadius: 12, background: KColors.primaryDim, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <i data-lucide={icon} style={{ width: 22, height: 22, color: KColors.primaryLight }}></i>
      </div>
      <div style={{ fontSize: 16, fontWeight: 700, color: KColors.fg1 }}>{title}</div>
      {description && <div style={{ fontSize: 13, color: KColors.fg3, maxWidth: 420, lineHeight: 1.55 }}>{description}</div>}
      {actionLabel && onAction && <KButton onClick={onAction}>{actionLabel}</KButton>}
      {secondaryLabel && onSecondary && (
        <KButton variant="ghost" size="sm" onClick={onSecondary}>{secondaryLabel}</KButton>
      )}
    </div>
  );
}

// ── Setup checklist ───────────────────────────────────
function SetupChecklist({ checklist, onNavigate, compact = false }) {
  const items = [
    { key: 'treasury', label: 'Set up treasury', route: 'treasury' },
    { key: 'recipient', label: 'Add a contractor recipient', route: 'recipients' },
    { key: 'workflow', label: 'Create a payout workflow', route: 'workflows' },
    { key: 'firstRun', label: 'Run your first payout', route: 'workflows' },
  ];
  const doneCount = items.filter(i => checklist[i.key]).length;
  if (doneCount === items.length) return null;

  return (
    <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: compact ? '12px 14px' : '16px 18px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: compact ? 8 : 12 }}>
        <div style={{ fontSize: compact ? 12 : 13, fontWeight: 700, color: KColors.fg1 }}>Setup checklist</div>
        <span style={{ fontSize: 11, color: KColors.fg3 }}>{doneCount}/{items.length} complete</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {items.map(item => (
          <button
            key={item.key}
            type="button"
            onClick={() => onNavigate && onNavigate(item.route)}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 6,
              border: `1px solid ${KColors.border}`, background: KColors.raised, cursor: 'pointer',
              textAlign: 'left', fontFamily: 'inherit', width: '100%',
            }}
          >
            <span style={{ width: 18, height: 18, borderRadius: 4, border: `1px solid ${checklist[item.key] ? KColors.success : KColors.borderStrong}`, background: checklist[item.key] ? KColors.successBg : 'transparent', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: KColors.success, fontSize: 11 }}>
              {checklist[item.key] ? '✓' : ''}
            </span>
            <span style={{ fontSize: 12, color: checklist[item.key] ? KColors.fg3 : KColors.fg1, textDecoration: checklist[item.key] ? 'line-through' : 'none' }}>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Widget placeholder ────────────────────────────────
function KWidgetShell({ title, children, actionLabel, onAction }) {
  return (
    <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 16, display: 'flex', flexDirection: 'column', gap: 10, minHeight: 140 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <KSectionLabel>{title}</KSectionLabel>
        {actionLabel && onAction && <KButton variant="ghost" size="sm" onClick={onAction}>{actionLabel}</KButton>}
      </div>
      {children}
    </div>
  );
}

// ── Sidebar nav ───────────────────────────────────────
function KSidebar({ active, onNavigate, navItems }) {
  const items = navItems || [
    { id: 'runner',  icon: 'play-circle', label: 'Workflow runner' },
    { id: 'ai',      icon: 'cpu',         label: 'AI generator' },
    { id: 'builder', icon: 'git-branch',  label: 'Workflow builder' },
  ];
  return (
    <aside aria-label="Primary navigation" style={{ width: 220, background: KColors.raised, borderRight: `1px solid ${KColors.border}`, display: 'flex', flexDirection: 'column', flexShrink: 0 }}>
      {/* Logo */}
      <div style={{ padding: '18px 16px 16px', display: 'flex', alignItems: 'center', gap: 10, borderBottom: `1px solid ${KColors.border}` }}>
        <KLogo size={28}/>
        <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em', color: KColors.fg1 }}>kinetic</span>
      </div>
      {/* Nav */}
      <nav style={{ padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.map(item => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            aria-current={active === item.id ? 'page' : undefined}
            style={{
              display: 'flex', alignItems: 'center', gap: 9, padding: '8px 10px',
              borderRadius: 6, border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%',
              background: active === item.id ? KColors.primaryDim : 'transparent',
              color: active === item.id ? KColors.primaryLight : KColors.fg2,
              fontSize: 13, fontWeight: 500, fontFamily: 'inherit',
              transition: 'background 120ms ease-out, color 120ms ease-out',
            }}
          >
            <i data-lucide={item.icon} style={{ width: 15, height: 15, flexShrink: 0 }}></i>
            {item.label}
          </button>
        ))}
      </nav>
      {/* Footer */}
      <div style={{ marginTop: 'auto', padding: '12px 16px', borderTop: `1px solid ${KColors.border}` }}>
        <div style={{ fontSize: 11, color: KColors.fg3 }}>MVP · v0.1.0</div>
      </div>
    </aside>
  );
}

Object.assign(window, {
  KColors, KLogo, KButton, KInput, KSelect, KPill, KStepper, KStepsTable, KCodeBlock, KSectionLabel, KDivider, KSidebar,
  KEmptyState, SetupChecklist, KWidgetShell,
  WORKSPACE_STORAGE_KEY, CHECKLIST_STORAGE_PREFIX, DEFAULT_CHECKLIST,
  loadWorkspace, saveWorkspace, clearWorkspace, loadChecklist, saveChecklist, markChecklistStep,
});
