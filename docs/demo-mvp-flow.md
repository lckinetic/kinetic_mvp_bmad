# MVP Demo Flow

This is the canonical walkthrough for product demos after Epics 1-7 completion.

## Preconditions

- Backend is running locally (`MOCK_MODE=true`).
- UI kit is served from backend same-origin path: `http://127.0.0.1:8000/ui-kit`.
- Pick one mode before demo:
  - `cp backend/.env.mock.example backend/.env` for deterministic demo-safe mode
  - `cp backend/.env.live.example backend/.env` for real AI calls

## Demo path (happy path)

1. Open the UI and land on **Home**.
2. From Home, use the guided sequence cards to introduce the flow.
3. Navigate to **Workflows**.
4. Select **Managed Crypto Treasury** in the template list.
5. Click **Open in Workflows**.
6. In runner, review prefilled inputs and click **Run workflow**.
7. Confirm run result appears with:
   - run id
   - status
   - step table data
8. Navigate to **Operations** in the sidebar.
9. Open a recent run and confirm detail information is visible.
10. Navigate to **AI Assistant** and generate a workflow from a prompt.
11. Navigate to **Workflow Builder (mock)** and verify graph editing is reachable.

## Optional live-AI segment

1. Switch to live mode (`MOCK_MODE=false`) with valid `OPENAI_API_KEY`.
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
- If no runs appear from API, confirm backend is up and open the UI from `/ui-kit` (same origin).
- If styles/icons look incorrect, refresh once after startup and verify static assets loaded.
