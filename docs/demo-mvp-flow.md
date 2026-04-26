# MVP Demo Flow

This is the canonical walkthrough for product demos after Epics 1-7 completion.

## Preconditions

- Backend is running locally (`MOCK_MODE=true`).
- UI kit is served from `ui_kits/app/index.html` (or equivalent static host).
- Optional: set `window.KINETIC_API_BASE` to target a different backend origin.

## Demo path (happy path)

1. Open the UI and land on **Templates**.
2. Select **Managed Crypto Treasury** in the template list.
3. Click **Open in runner**.
4. In runner, review prefilled inputs and click **Run workflow**.
5. Confirm run result appears with:
   - run id
   - status
   - step table data
6. Navigate to **Runs** in the sidebar.
7. Open a recent run and confirm detail information is visible.
8. Navigate to **Assistant** and generate a workflow from a prompt.
9. Navigate to **Builder** and verify graph editing is reachable.

## Accessibility sanity checks (during demo)

- Use `Tab`/`Shift+Tab` to navigate actionable controls.
- Verify visible focus ring appears on focused controls.
- Use skip link (`Skip to main content`) at the top of the page.
- In Builder, focus a palette step and press `Enter` or `Space` to add it.

## Troubleshooting quick notes

- If API calls fail, UI falls back to deterministic local mock data for templates/runs and run completion.
- If no runs appear from API, confirm backend is up and `KINETIC_API_BASE` is correct.
- If styles/icons look incorrect, refresh once after startup and verify static assets loaded.
