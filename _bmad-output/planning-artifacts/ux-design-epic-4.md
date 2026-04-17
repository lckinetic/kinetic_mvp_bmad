# UX Design Specification - Epic 4 (Customer Web App)

## Purpose

This UX artifact closes the planning gap noted in `prd-validation-report.md` and provides implementation-ready UX direction for Epic 4 without over-specifying visual details.

Primary scope:
- Story 4.1: App shell and navigation
- Story 4.2: Template browse and run (MOCK_MODE)
- Story 4.3: Accessibility baseline

## Inputs and Constraints

- Product requirements and journeys from `prd.md` (Maya UI, Alex chat handoff, Raj API parity, Jordan/Sam supportability).
- Epic definitions and acceptance criteria from `epics.md` (Epic 4).
- Architecture boundaries from `architecture.md` and `docs/architecture-layers.md`:
  - UI talks to API only.
  - API/OpenAPI remains source-of-truth for workflow start/status behavior.

## UX Outcomes

- A user can move from app entry to template discovery, run initiation, and run status tracking with no dead ends.
- UI behavior is consistent with API outcomes (same status semantics, same error meaning).
- Core paths are keyboard-usable and accessible to baseline standards.

## Information Architecture

### Top-level navigation

- `Templates`
- `Runs`
- `Assistant`

### Route map (MVP)

- `/app/templates` - template catalog
- `/app/templates/{template_name}` - template details and run form
- `/app/runs` - run history list
- `/app/runs/{run_id}` - run detail, status, metrics, steps
- `/app/assistant` - assistant entry and proposal handoff

### Navigation rules

- Primary nav is persistent in app shell.
- Each list has a deterministic detail destination.
- Every detail page exposes a clear "Back to list" and next action.

## Primary User Flows

### Flow A: Template discovery -> run start -> run status

1. User opens `Templates`.
2. User filters/scans templates and selects one.
3. User reviews template metadata and enters input.
4. User starts run.
5. UI navigates to run detail and shows state transitions until terminal status.

### Flow B: Run history triage

1. User opens `Runs`.
2. User filters by template/status.
3. User opens failed run.
4. User reviews error, metrics, and step timeline.

### Flow C: Assistant handoff to UI

1. User opens `Assistant`.
2. User gets proposal from chat.
3. User selects "Edit in UI".
4. UI lands on template/run builder context with mapped structure.

## Interaction Contracts (State Handling)

### Templates

- Loading: skeleton list and disabled filters.
- Empty: "No templates found" with reset action.
- Error: retry affordance and short actionable message.
- Success: deterministic card/list rows with primary action "Use template".

### Run start

- Validation: inline field errors before submit.
- Submit pending: disable submit, show progress indicator.
- Submit success: route to run detail with run ID.
- Submit error: message mirrors API semantics; avoid stack traces.

### Run status and steps

- Running: live/refresh state visible and non-blocking.
- Completed: show output and metrics summary.
- Failed: show clear failure reason and step-level failure location.
- Unknown/not found: standard empty/error surface with recovery action.

## UI/API Parity Rules

- UI run states must use canonical values and meanings used by API.
- Error messaging in UI should map to API error envelope semantics (code/message/details when available).
- Template metadata displayed in UI should come from workflow template endpoints, not duplicated constants.
- Run detail and steps should reflect API response fields directly to reduce drift.

## Accessibility Baseline (Story 4.3)

- Keyboard:
  - All nav links, filters, buttons, and table rows reachable by Tab.
  - Visible focus indicator on all interactive controls.
  - No keyboard trap in dialogs/drawers.
- Structure:
  - One `h1` per page; hierarchical headings.
  - Landmarks: nav/main/footer where applicable.
- Forms:
  - Label + helper/error association for each input.
  - Error text announced and visible.
- Feedback:
  - Status updates and errors announced via accessible live region.

## Story-to-UX Mapping

### Story 4.1 (App shell & navigation)

- Deliver top-level nav, route map, and no-dead-end transitions between templates/runs/assistant.
- UX acceptance evidence:
  - Route transitions complete for list/detail paths.
  - Back navigation and primary actions available on each page.

### Story 4.2 (Template browse & run)

- Deliver template catalog, template detail, and run initiation UX in MOCK_MODE.
- UX acceptance evidence:
  - User can start run from UI and reach status visibility through completion/failure.
  - Errors are actionable and consistent with API semantics.

### Story 4.3 (Accessibility baseline)

- Deliver keyboard + focus + semantic structure + form feedback baseline.
- UX acceptance evidence:
  - Manual keyboard pass for core flows.
  - Accessibility checks pass for critical interactions.

## Handoff Checklist for Implementation

- [ ] Routes and nav labels implemented per IA.
- [ ] All primary flow states implemented (loading/empty/error/success).
- [ ] Run lifecycle surfaces canonical status progression.
- [ ] Assistant entry includes explicit handoff action to UI.
- [ ] Keyboard navigation and visible focus verified on core flows.
- [ ] UI behaviors documented for QA test cases.

## Out of Scope (This Artifact)

- Pixel-perfect visual system and final branding spec.
- Advanced responsive layouts beyond MVP baseline behavior.
- Full design system tokenization.
