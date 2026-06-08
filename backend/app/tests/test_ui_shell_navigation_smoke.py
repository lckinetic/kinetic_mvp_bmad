"""Lightweight smoke checks for app-shell navigation wiring."""

from __future__ import annotations

from pathlib import Path


def _index_html() -> str:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "ui_kits" / "app" / "index.html").read_text(encoding="utf-8")


def test_app_shell_declares_operational_nav_routes() -> None:
    content = _index_html()
    assert "id: 'dashboard'" in content
    assert "id: 'treasury'" in content
    assert "id: 'recipients'" in content
    assert "id: 'activity'" in content
    assert "id: 'settings'" in content


def test_legacy_demo_routes_remain_addressable() -> None:
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


def test_workspace_bootstrap_defaults_to_dashboard_when_present() -> None:
    content = _index_html()
    assert "loadWorkspace() ? 'dashboard' : 'home'" in content


def test_dashboard_refreshes_treasury_balance_on_return() -> None:
    content = _index_html()
    assert "dashboardRefreshKey" in content
    assert "refreshKey={dashboardRefreshKey}" in content
    dashboard = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "Dashboard.jsx").read_text(encoding="utf-8")
    assert "acknowledgeAlert" in dashboard
    assert "prominentAlerts" in dashboard


def test_operational_screens_wire_checklist_progression() -> None:
    content = _index_html()
    assert "onChecklistStep={completeChecklistStep}" in content
    treasury = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "Treasury.jsx").read_text(encoding="utf-8")
    recipients = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "Recipients.jsx").read_text(encoding="utf-8")
    ops_shell = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "OpsShell.jsx").read_text(encoding="utf-8")
    assert "onChecklistStep('treasury')" in treasury
    assert "Copy funding address" in treasury
    assert "onChecklistStep('recipient')" in recipients
    assert "Save recipient" in recipients
    picker = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "RecipientPicker.jsx").read_text(encoding="utf-8")
    ai_generator = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "AIGenerator.jsx").read_text(encoding="utf-8")
    assert "RecipientPicker" in picker
    assert "resolveRecipientValue" in picker
    assert "<RecipientPicker" in ops_shell
    assert "<RecipientPicker" in ai_generator
    assert "Pay Alice 50 USDC every Friday" in ai_generator
    assert "Save as payout workflow" in ai_generator
    assert "/ai/payout-draft" in ai_generator
    assert "Add recipient" in ai_generator
    assert "onNavigate('recipients')" in ai_generator
    assert "Create payout workflow" in ops_shell
    assert "onChecklistStep('firstRun')" in ops_shell
    activity = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "Activity.jsx").read_text(encoding="utf-8")
    assert "ACTIVITY_API" in activity
    assert "Event detail" in activity
    assert "activityRequest('/event-types')" in activity
    assert "FALLBACK_EVENT_TYPE_OPTIONS" in activity
    assert "CONTRACTOR_PAYOUT_STEP_LABELS" in ops_shell
    assert "formatLastRun" in ops_shell
    assert "Last run" in ops_shell
    workflow_runner = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "WorkflowRunner.jsx").read_text(encoding="utf-8")
    assert "name: 'contractor_payout'" in workflow_runner
    assert "recipientsRequest('/networks')" in recipients


def test_home_use_cases_align_with_treasury_payout_hero() -> None:
    home = (Path(__file__).resolve().parents[3] / "ui_kits" / "app" / "Home.jsx").read_text(encoding="utf-8")
    assert "Weekly contractor payouts" in home
    assert "Treasury, Recipients, Workflows, Activity Centre shells" in home
    assert "Runner, AI Generator, Builder" not in home
