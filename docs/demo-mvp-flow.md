# MVP Demo Flow

This is the canonical walkthrough for product demos after Phase 2 Sprint 1 (hero workflow shell).

## Preconditions

- Backend is running locally (`MOCK_MODE=true`).
- UI kit is served from backend same-origin path: `http://127.0.0.1:8000/ui-kit`.
- Pick one mode before demo:
  - `cp backend/.env.mock.example backend/.env` for deterministic demo-safe mode
  - `cp backend/.env.live.example backend/.env` for real AI calls

## Demo path (hero journey — Sprint 1)

1. Open the UI and land on **Home** (programmable financial operations positioning).
2. Click **Get started** to open the onboarding wizard.
3. Complete onboarding: audience → preview → create workspace → **Go to Dashboard**.
4. On **Dashboard**, review the setup checklist (treasury, recipients, workflow, activity).
5. Navigate to **Treasury** → **Create treasury wallet**.
6. Use **Simulate deposit** (mock mode) to fund the treasury, then confirm balance and transaction history update.
7. Optionally click **Check payout readiness** to see the insufficient-balance guidance when unfunded.
8. Navigate to **Recipients** → **Add recipient** (name, network, wallet address) and confirm the directory list updates.
9. Navigate to **Workflows** → **Create payout workflow** (recipient, amount, schedule) → **Run now**.
10. Confirm treasury balance decreases and the run completes with step-level success messaging.
11. Navigate to **Activity Centre** — confirm deposit, payout, and workflow events appear in the timeline.
12. Open an event detail drawer and use cross-links to treasury or workflows.
13. Return to **Dashboard** and confirm recent activity shows the latest events.
14. Trigger a blocked payout (run workflow with insufficient balance) and confirm an alert appears on the Dashboard with **Fund treasury** recovery guidance.
15. Acknowledge the alert and confirm it is de-emphasized; open **Activity Centre** and confirm a **Payout blocked** event appears for the failed run attempt.
16. Open **Settings** → **Advanced** → **AI Assistant** (or navigate via legacy tools).
17. In **Payout workflow** mode, try **Pay Alice 50 USDC every Friday** — confirm draft shows amount, schedule, and matched recipient.
18. Edit the draft if needed, then **Save as payout workflow** (no auto-run). Open **Workflows** and run the saved workflow.
19. Open **Settings** → **Advanced** to reach other legacy MVP tools if needed.

## Legacy demo path (regression)

1. From **Settings** → **Advanced**, open **Legacy templates**.
2. Select **Managed Crypto Treasury** in the template list.
3. Click **Run workflow** and complete a run in the runner.
4. Open **Legacy operations** and confirm run detail is visible.
5. Open **AI Assistant** → **Advanced graph** and generate a legacy graph workflow from a prompt.
6. Open **Workflow Builder (mock)** and verify graph editing is reachable.

## Optional live-AI segment

1. Switch to live mode (`AI_MOCK_MODE=false`) with valid `OPENAI_API_KEY`.
2. Restart backend.
3. In **AI Assistant**, submit a natural-language request and generate/run.
4. Verify shell badge shows `LIVE AI` and model name.

## Accessibility sanity checks (during demo)

- Use `Tab`/`Shift+Tab` to navigate actionable controls.
- Verify visible focus ring appears on focused controls.
- Use skip link (`Skip to main content`) at the top of the page.
- In Workflow Builder, focus a palette step and press `Enter` or `Space` to add it.

## Troubleshooting quick notes

- If API calls fail, UI falls back to deterministic local mock data for templates/runs and run completion.
- If workspace creation fails, confirm backend is up and `DATABASE_URL` is reachable locally (use SQLite override if Railway URL is set).
- If no runs appear from API, confirm backend is up and open the UI from `/ui-kit` (same origin).
- If styles/icons look incorrect, refresh once after startup and verify static assets loaded.
