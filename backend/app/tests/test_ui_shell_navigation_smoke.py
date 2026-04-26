"""Lightweight smoke checks for app-shell navigation wiring."""

from __future__ import annotations

from pathlib import Path


def _index_html() -> str:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "ui_kits" / "app" / "index.html").read_text(encoding="utf-8")


def test_app_shell_declares_expected_top_level_routes() -> None:
    content = _index_html()
    assert "id: 'templates'" in content
    assert "id: 'runs'" in content
    assert "id: 'assistant'" in content
    assert "id: 'builder'" in content


def test_templates_nav_resets_runner_subview() -> None:
    content = _index_html()
    assert "setTemplateOpenInRunner(false);" in content
    assert "if (next === 'templates') setRunnerTemplateName(null);" in content


def test_hash_route_sync_is_present() -> None:
    content = _index_html()
    assert "window.addEventListener('hashchange', onHashChange);" in content
    assert "window.location.hash = `#${page}`;" in content
