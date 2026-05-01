// Kinetic — Home / Landing Screen

function StatCard({ value, label, sub }) {
  return (
    <div style={{ flex: 1, minWidth: 140, background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 8, padding: '20px 20px 16px' }}>
      <div style={{ fontSize: 32, fontWeight: 700, letterSpacing: '-0.03em', color: KColors.fg1, lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: 12, fontWeight: 600, color: KColors.fg2, marginTop: 4 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: KColors.fg3, marginTop: 3, lineHeight: 1.4 }}>{sub}</div>}
    </div>
  );
}

function PainPoint({ children }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 0', borderBottom: `1px solid ${KColors.border}` }}>
      <div style={{ width: 4, height: 4, borderRadius: '50%', background: KColors.error, marginTop: 7, flexShrink: 0 }}/>
      <div style={{ fontSize: 13, fontWeight: 500, color: KColors.fg1, lineHeight: 1.45 }}>{children}</div>
    </div>
  );
}

function SolutionPoint({ children }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 0', borderBottom: `1px solid ${KColors.border}` }}>
      <div style={{ width: 4, height: 4, borderRadius: '50%', background: KColors.success, marginTop: 7, flexShrink: 0 }}/>
      <div style={{ fontSize: 13, fontWeight: 500, color: KColors.fg1, lineHeight: 1.45 }}>{children}</div>
    </div>
  );
}

function ScreenCard({ step, title, icon, description, hint, tag, onClick }) {
  const [hovered, setHovered] = React.useState(false);
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        flex: 1, minWidth: 200, background: KColors.overlay,
        border: `1px solid ${hovered ? KColors.primary : KColors.border}`,
        borderRadius: 10, padding: 20, cursor: 'pointer',
        transition: 'border-color 150ms, box-shadow 150ms',
        boxShadow: hovered ? `0 0 0 2px ${KColors.primaryDim}` : 'none',
        display: 'flex', flexDirection: 'column', gap: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: KColors.primaryDim, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <i data-lucide={icon} style={{ width: 16, height: 16, color: KColors.primaryLight }}></i>
        </div>
        <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 10, color: KColors.fg3, background: KColors.raised, padding: '2px 7px', borderRadius: 4, border: `1px solid ${KColors.border}` }}>Step {step}</span>
      </div>
      <div>
        <div style={{ fontSize: 14, fontWeight: 700, color: KColors.fg1, marginBottom: 4 }}>{title}</div>
        <div style={{ fontSize: 12, color: KColors.fg3, lineHeight: 1.55 }}>{description}</div>
      </div>
      <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 11, color: KColors.fg3, fontStyle: 'italic' }}>{hint}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, fontWeight: 600, color: KColors.primaryLight }}>
          Open <i data-lucide="arrow-right" style={{ width: 12, height: 12 }}></i>
        </div>
      </div>
    </div>
  );
}

function LayerCard({ label, tag, bullets, color }) {
  return (
    <div style={{ flex: 1, background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
      <div style={{ background: `rgba(${color}, 0.1)`, borderBottom: `1px solid ${KColors.border}`, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: KColors.fg1 }}>{label}</div>
        <span style={{ fontSize: 10, fontWeight: 600, color: `rgb(${color})`, background: `rgba(${color}, 0.15)`, padding: '2px 8px', borderRadius: 4, letterSpacing: '0.05em', textTransform: 'uppercase' }}>{tag}</span>
      </div>
      <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
        {bullets.map((b, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <span style={{ color: `rgb(${color})`, fontSize: 12, marginTop: 1 }}>✦</span>
            <span style={{ fontSize: 12, color: KColors.fg2, lineHeight: 1.5 }}>{b}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function UseCaseCard({ segment, useCase, prompt, steps }) {
  return (
    <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', borderBottom: `1px solid ${KColors.border}` }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: KColors.fg3, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>{segment}</div>
        <div style={{ fontSize: 13, fontWeight: 700, color: KColors.fg1 }}>{useCase}</div>
      </div>
      <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div style={{ background: KColors.raised, borderRadius: 6, padding: '8px 10px', border: `1px solid ${KColors.border}` }}>
          <div style={{ fontSize: 10, color: KColors.fg3, fontWeight: 600, marginBottom: 4, letterSpacing: '0.04em' }}>AI PROMPT</div>
          <div style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: KColors.primaryLight, lineHeight: 1.5, fontStyle: 'italic' }}>"{prompt}"</div>
        </div>
        {steps && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {steps.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 10, color: KColors.fg3, width: 14, flexShrink: 0 }}>{i+1}.</span>
                <span style={{ fontSize: 11, fontWeight: 500, color: KColors.fg1 }}>{s}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function RoadmapStep({ phase, title, items, active }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: active ? KColors.success : KColors.border, border: `2px solid ${active ? KColors.success : KColors.borderStrong}`, flexShrink: 0 }}/>
        <div style={{ height: 1, flex: 1, background: KColors.border }}/>
      </div>
      <div style={{ fontSize: 10, fontWeight: 600, color: active ? KColors.success : KColors.fg3, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 4 }}>{phase}</div>
      <div style={{ fontSize: 13, fontWeight: 700, color: KColors.fg1, marginBottom: 10 }}>{title}</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {items.map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 7 }}>
            <span style={{ color: active ? KColors.success : KColors.fg3, fontSize: 11, marginTop: 1 }}>{active ? '✓' : '→'}</span>
            <span style={{ fontSize: 12, color: KColors.fg2, lineHeight: 1.5 }}>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SectionHeading({ label, title, sub }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ fontSize: 10, fontWeight: 600, color: KColors.primary, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em', color: KColors.fg1, marginBottom: 6 }}>{title}</div>
      {sub && <div style={{ fontSize: 13, color: KColors.fg3, maxWidth: 560, lineHeight: 1.6 }}>{sub}</div>}
    </div>
  );
}

function Home({ onNavigate }) {
  return (
    <div style={{ height: '100%', overflow: 'auto', background: KColors.surface }}>
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '40px 32px 80px' }}>

        {/* ── HERO ── */}
        <div style={{ marginBottom: 56 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: KColors.successBg, color: KColors.success, fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 9999, border: '1px solid rgba(74,222,128,0.2)' }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: KColors.success }}/>
              MVP LIVE
            </span>
            <span style={{ fontSize: 11, color: KColors.fg3 }}>Banxa · Privy · Coinbase · Fireblocks</span>
          </div>
          <h1 style={{ fontSize: 42, fontWeight: 700, letterSpacing: '-0.03em', color: KColors.fg1, lineHeight: 1.15, marginBottom: 16, maxWidth: 640 }}>
            Digital &amp; crypto operations,<br/>
            <span style={{ color: KColors.primaryLight }}>as simple as consumer apps.</span>
          </h1>
          <p style={{ fontSize: 15, color: KColors.fg2, maxWidth: 560, lineHeight: 1.65, marginBottom: 28 }}>
            Kinetic is an AI-powered workflow automation platform for crypto operations. Build, run, and monitor end-to-end crypto workflows across trading, treasury, custody, and payments — without custom integrations.
          </p>
          <div style={{ display: 'flex', gap: 10 }}>
            <KButton onClick={() => onNavigate('builder')}>
              <i data-lucide="git-branch" style={{ width: 14, height: 14 }}></i>
              Build a workflow
            </KButton>
            <KButton variant="secondary" onClick={() => onNavigate('assistant')}>
              <i data-lucide="cpu" style={{ width: 14, height: 14 }}></i>
              Try AI Assistant
            </KButton>
            <KButton variant="secondary" onClick={() => onNavigate('templates')}>
              <i data-lucide="play-circle" style={{ width: 14, height: 14 }}></i>
              Browse templates
            </KButton>
          </div>
        </div>

        {/* ── STATS ── */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 56, flexWrap: 'wrap' }}>
          <StatCard value="$40B+" label="Web3 market by 2030" sub="Growing at 44% CAGR"/>
          <StatCard value="350M+" label="SMEs globally" sub="Discovering crypto operations"/>
          <StatCard value="$15–25K" label="Per integration, per provider" sub="And months to deploy"/>
          <StatCard value="Sandbox" label="Current mode" sub="Live integrations in progress"/>
        </div>

        {/* ── PROBLEM / SOLUTION ── */}
        <div style={{ marginBottom: 56 }}>
          <SectionHeading label="The problem" title="Building crypto capabilities is too hard." sub="Companies want crypto features. The infrastructure to build them is fragmented, expensive, and slow."/>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: KColors.error, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 12 }}>Current pain points</div>
              <PainPoint>No in-house crypto expertise</PainPoint>
              <PainPoint>Fragmented tools across trading, custody &amp; payments</PainPoint>
              <PainPoint>Each integration takes months and costs $15–25K</PainPoint>
              <PainPoint>Manual processes create errors and delays</PainPoint>
            </div>
            <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: KColors.success, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 12 }}>Kinetic's solution</div>
              <SolutionPoint>Plug &amp; play backend — no dev team needed</SolutionPoint>
              <SolutionPoint>One platform for all crypto operations</SolutionPoint>
              <SolutionPoint>Pre-built flows, ready to deploy instantly</SolutionPoint>
              <SolutionPoint>AI-assisted, no-code workflow automation</SolutionPoint>
            </div>
          </div>
        </div>

        {/* ── HOW TO USE THIS PLATFORM ── */}
        <div style={{ marginBottom: 56 }}>
          <SectionHeading
            label="Getting started"
            title="Four screens. One platform."
            sub="Use each screen for a different mode of operation — or follow the sequence from templates to monitoring to AI to custom building."
          />
          {/* Connector line */}
          <div style={{ position: 'relative', display: 'flex', gap: 12 }}>
            <div style={{ position: 'absolute', top: 16, left: 32, right: 32, height: 1, background: `linear-gradient(90deg, ${KColors.primary}40, ${KColors.primary}40)`, zIndex: 0, pointerEvents: 'none' }}/>
            <ScreenCard
              step={1}
              icon="play-circle"
              title="Workflows"
              description="Select a pre-built template — Treasury Rebalance, Managed Crypto Treasury, and more. Fill in inputs and execute with one click. Track step-by-step progress in real time."
              hint="Best for: standard operations"
              onClick={() => onNavigate('templates')}
            />
            <ScreenCard
              step={2}
              icon="activity"
              title="Operations"
              description="View the full history of all workflow runs. Drill into any run to inspect step-level status, duration metrics, execution logs, and output payloads."
              hint="Best for: monitoring & audit"
              onClick={() => onNavigate('runs')}
            />
            <ScreenCard
              step={3}
              icon="cpu"
              title="AI Assistant"
              description="Describe any workflow in plain English. The AI interprets your intent, generates a structured workflow graph you can review and edit, then runs it end-to-end."
              hint="Best for: custom operations"
              onClick={() => onNavigate('assistant')}
            />
            <ScreenCard
              step={4}
              icon="git-branch"
              title="Workflow Builder"
              description="Drag and drop steps from the palette onto the canvas. Connect nodes to define execution order, edit parameters inline, and export as JSON."
              hint="Best for: visual composition"
              onClick={() => onNavigate('builder')}
            />
          </div>
          <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
            <i data-lucide="info" style={{ width: 13, height: 13, color: KColors.fg3 }}></i>
            <span style={{ fontSize: 12, color: KColors.fg3 }}>All screens run in <span style={{ fontFamily: 'IBM Plex Mono, monospace', fontSize: 11, color: KColors.fg2, background: KColors.overlay, padding: '1px 6px', borderRadius: 3, border: `1px solid ${KColors.border}` }}>MOCK MODE</span> — no real transactions are executed until live accounts are connected.</span>
          </div>
        </div>

        {/* ── PRODUCT ARCHITECTURE ── */}
        <div style={{ marginBottom: 56 }}>
          <SectionHeading label="Architecture" title="Two-layer platform." sub="API Fabric handles integrations. Web3Flow handles orchestration. Together they turn complex crypto operations into simple, repeatable workflows."/>
          <div style={{ display: 'flex', gap: 12 }}>
            <LayerCard
              label="Layer 1 — API Fabric"
              tag="Infrastructure"
              color="59,130,246"
              bullets={[
                'Trading venues — Coinbase, Kraken, Binance',
                'Custody solutions — Fireblocks, Copper',
                'DeFi protocols — Aave, Lido, Uniswap',
                'On-ramps — Banxa, MoonPay, Transak',
                'Payment networks — Stripe, Ripple, Bitpay',
              ]}
            />
            <LayerCard
              label="Layer 2 — Web3Flow"
              tag="Automation"
              color="91,95,245"
              bullets={[
                'Visual workflow builder (drag & drop)',
                'Pre-built workflow templates',
                'AI assistant — natural language → runnable workflow',
                'Real-time monitoring & audit logs',
                'Custom logic support — if/then conditions',
              ]}
            />
          </div>
        </div>

        {/* ── USE CASES ── */}
        <div style={{ marginBottom: 56 }}>
          <SectionHeading label="Use cases" title="From idea to deployment in minutes." sub="No developers. No months of integrations. No compromise on security."/>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <UseCaseCard
              segment="SMEs & Financial Institutions"
              useCase="Operating model design"
              prompt="Define my crypto strategy and show example workflows."
              steps={['AI analyzes goals', 'Generates operating model', 'Proposes workflow templates']}
            />
            <UseCaseCard
              segment="Crypto-native SMEs"
              useCase="Treasury diversification"
              prompt="Accumulate ETH and earn yield on idle assets."
              steps={['Onramp fiat → USDC', 'Trade to ETH via Coinbase', 'Custody at Fireblocks', 'Stake via Lido (optional)']}
            />
            <UseCaseCard
              segment="Fintechs & PSPs"
              useCase="Stablecoin rewards"
              prompt="Reward users who deposit over a set threshold."
              steps={['Onramp stablecoin', 'Monitor deposit threshold', 'Trigger reward payout', 'Send notification']}
            />
          </div>
        </div>

        {/* ── ROADMAP ── */}
        <div style={{ marginBottom: 0 }}>
          <SectionHeading label="Roadmap" title="Where we're headed." sub="Sandbox MVP is live. Investment unlocks real transactions, production-grade flows, and US market launch."/>
          <div style={{ background: KColors.overlay, border: `1px solid ${KColors.border}`, borderRadius: 10, padding: '28px 28px 24px' }}>
            <div style={{ display: 'flex', gap: 24 }}>
              <RoadmapStep
                phase="Today"
                title="Sandbox MVP"
                active={true}
                items={[
                  'Workflow engine with prebuilt templates',
                  'AI assistant — natural language → workflow',
                  'Sandbox: Banxa, Privy, Coinbase',
                  'Full UI: Runner, AI Generator, Builder',
                  'FastAPI backend · PostgreSQL',
                ]}
              />
              <RoadmapStep
                phase="6–12 months"
                title="Go Live — Real Users"
                active={false}
                items={[
                  'Live transactions with real accounts',
                  'Onboard first paying customers',
                  'Production-grade security & compliance',
                  'CTO + engineering team in place',
                ]}
              />
              <RoadmapStep
                phase="Q4 2026"
                title="Series A"
                active={false}
                items={[
                  'Proven product-market fit',
                  'Capital raise — Series A',
                  'International expansion',
                  'White-label partner program',
                ]}
              />
            </div>
          </div>
        </div>

        {/* ── FOOTER ── */}
        <div style={{ marginTop: 48, paddingTop: 24, borderTop: `1px solid ${KColors.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <KLogo size={22}/>
            <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 14, letterSpacing: '-0.02em', color: KColors.fg1 }}>kinetic</span>
          </div>
          <div style={{ fontSize: 11, color: KColors.fg3 }}>September 2025 · Confidential</div>
        </div>

      </div>
    </div>
  );
}

Object.assign(window, { Home });
