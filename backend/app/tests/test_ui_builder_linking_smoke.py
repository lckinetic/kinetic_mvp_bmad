"""Lightweight smoke checks for builder node-linking wiring."""

from __future__ import annotations

from pathlib import Path


def _builder_jsx() -> str:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "ui_kits" / "app" / "WorkflowBuilder.jsx").read_text(encoding="utf-8")


def test_builder_properties_panel_exposes_connection_controls() -> None:
    content = _builder_jsx()
    assert "<KSectionLabel>Connections</KSectionLabel>" in content
    assert "Target step" in content
    assert "Select target step" in content
    assert "aria-label={`Remove link to ${target?.label || edge.to}`}" in content


def test_builder_connection_handlers_exist_and_are_wired() -> None:
    content = _builder_jsx()
    assert "function addEdge(fromId, toId) {" in content
    assert "function removeEdge(edgeId) {" in content
    assert "onAddEdge={addEdge}" in content
    assert "onRemoveEdge={removeEdge}" in content
