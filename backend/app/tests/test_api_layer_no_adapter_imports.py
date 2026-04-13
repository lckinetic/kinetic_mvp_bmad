"""Guard: API route modules must not import app.adapters directly (see docs/architecture-layers.md)."""

from __future__ import annotations

import ast
from pathlib import Path


def _api_py_files() -> list[Path]:
    api_dir = Path(__file__).resolve().parents[1] / "api"
    return sorted(api_dir.rglob("*.py"))


def _violations_for(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "app.adapters" or mod.startswith("app.adapters."):
                out.append(f"{path.relative_to(path.parents[2])}:{node.lineno} from {mod}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name == "app.adapters" or name.startswith("app.adapters."):
                    out.append(f"{path.relative_to(path.parents[2])}:{node.lineno} import {name}")
    return out


def test_api_modules_do_not_import_app_adapters() -> None:
    all_violations: list[str] = []
    for path in _api_py_files():
        all_violations.extend(_violations_for(path))
    assert not all_violations, "API layer must not import app.adapters:\n" + "\n".join(all_violations)
