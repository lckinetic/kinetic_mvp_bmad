# Deferred work

## Deferred from: code review of 1-1-module-boundary-audit-targeted-refactors.md (2026-04-13)

- AST import guard in `backend/app/tests/test_api_layer_no_adapter_imports.py` only catches static `import` / `from` forms; dynamic loaders (`importlib`, string module paths) can bypass while still violating intended layering. Optional follow-up: `import-linter` or targeted runtime checks.
