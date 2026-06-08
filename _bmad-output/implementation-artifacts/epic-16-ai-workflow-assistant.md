# Epic 16: AI workflow assistant (hero payout templates)

## Status
done

## Epic goal
Natural language → editable hero payout workflow draft with confirm-before-save; `AI_MOCK_MODE` independent of adapter mock mode.

## Stories implemented

### 16.1 — Hero payout NL schema & prompt
- `normalize_payout_draft()` in `backend/app/ai/payout_draft.py`
- OpenAI `PAYOUT_SYSTEM_PROMPT` in `backend/app/ai/service.py`

### 16.2 — Mock AI payout draft generator
- `parse_payout_draft_mock()` with deterministic parsing for hero demo prompts
- `_extract_recipient_name()` supports `pay/send <Name>` and `to <Name>` patterns
- `_extract_monthly_day()` avoids amount substring false matches (e.g. `100` → `10`)

### 16.3 — Recipient name resolution
- `resolve_recipient_for_draft()` in `backend/app/ai/payout_resolver.py`
- Exact, partial, first-name match; ambiguous match warnings; `recipient_id` override

### 16.4 — AI draft review UI
- `ui_kits/app/AIGenerator.jsx` payout mode: editable name, amount, asset, schedule, recipient
- **Add recipient** CTA when resolution fails; no auto-run

### 16.5 — Save AI draft as WorkflowDefinition
- **Save as payout workflow** → `POST /payout-workflows` with E13 validation
- Integration test: draft → save → workflow with schedule/recipient

### 16.6 — AI Assistant hero context & examples
- `HERO_EXAMPLE_PROMPTS` in payout mode (default tab)
- Route subtitle updated for payout-draft vocabulary
- Accessible via Settings → Advanced → AI Assistant

### 16.7 — Live OpenAI path & error handling
- `OpenAIAiService.generate_payout_draft()` via chat completions
- Sanitized `AI_PAYOUT_DRAFT_FAILED` (502); secrets redacted in error details

## API
- `POST /ai/payout-draft` — NL message + optional `recipient_id` → editable draft
- `GET /ai/capabilities` — includes `payout_draft_supported`

## Tests
- `backend/app/tests/test_payout_draft_api.py` — mock parse, roster, override, Bob monthly, ambiguous recipient, save integration, error envelope, main mount
- `backend/app/tests/test_ai_mode_switching.py` — AI mock decoupling, interpret errors
- `backend/app/tests/test_ui_shell_navigation_smoke.py` — AIGenerator hero wiring

## Demo alignment
- `docs/demo-mvp-flow.md` steps 16–18 (Settings → AI Assistant → generate → save → Workflows)

## Review findings (resolved)

### Medium (fixed)
- [x] Bob monthly hero example broken in mock parser → `to <Name>` + anchored monthly day extraction
- [x] No Add recipient CTA when unresolved → button in draft review panel
- [x] No save-as-workflow integration test → `test_save_payout_draft_creates_workflow_definition`
- [x] Stale Settings Sprint 2 copy → updated environment description

### Low (fixed)
- [x] Ambiguous recipient resolution untested → `test_payout_draft_ambiguous_recipient_requires_manual_selection`
- [x] Generic assistant route subtitle → payout-draft copy
- [x] Thin smoke coverage → hero prompts, save CTA, payout-draft API asserts
- [x] Dead `is_payout_intent()` → removed
- [x] No epic artifact → this file

### Deferred
- [ ] Live OpenAI payout-draft httpx integration test (explosion/sanitization covered)

### Also fixed (follow-up)
- [x] Home marketing layer copy → editable payout workflow draft (UX-14 overlap)
