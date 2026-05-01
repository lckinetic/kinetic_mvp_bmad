# Story 9.1: Decouple AI mock-mode from global mock-mode

## Status
done

## Story
As a developer, I want AI service mock/real behavior to be controlled by a dedicated flag (`AI_MOCK_MODE`) instead of only the global `MOCK_MODE`, so that I can test live OpenAI behavior without forcing Banxa/Privy/Coinbase into real mode.

## Scope implemented
- Added `ai_mock_mode` to settings/config and resolved its value from `AI_MOCK_MODE` with fallback to `MOCK_MODE`.
- Updated AI startup validation checks to key off AI mode behavior instead of global adapter mode.
- Updated AI service selection logic to branch on `settings.ai_mock_mode`.
- Added `AI_MOCK_MODE` to local environment configuration with explanatory comment.

## Acceptance criteria check
1. AI mode can be explicitly controlled independently from adapter mock mode: **pass**
2. Backward compatibility is preserved when `AI_MOCK_MODE` is unset (fallback to `MOCK_MODE`): **pass**
3. Live AI validation gates apply according to AI mode: **pass**
4. Adapter runtime behavior remains unchanged by this story: **pass**

## Notes
- This story intentionally isolates AI mode control to enable safe live-model testing while adapter integrations remain in mock paths.
