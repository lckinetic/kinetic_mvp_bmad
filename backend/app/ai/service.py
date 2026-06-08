from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.ai.interpreter import interpret_request
from app.ai.payout_draft import normalize_payout_draft, parse_payout_draft_mock
from app.core.config import Settings


def _extract_json_object(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned non-JSON response: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Model response must be a JSON object.")
    return payload


def _normalize_workflow(payload: dict[str, Any]) -> dict[str, Any]:
    steps = payload.get("steps") or []
    if not isinstance(steps, list):
        steps = []
    normalized_steps: list[dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        step_type = str(step.get("type") or "").strip()
        if not step_type:
            continue
        params = step.get("params")
        if not isinstance(params, dict):
            params = {}
        normalized_steps.append(
            {
                "id": str(step.get("id") or f"step_{idx}"),
                "type": step_type,
                "params": params,
            }
        )
    if not normalized_steps:
        normalized_steps = interpret_request("create wallet").get("steps", [])
    return {
        "workflow_name": str(payload.get("workflow_name") or "generated_workflow"),
        "business_summary": str(payload.get("business_summary") or "Generated workflow from AI request."),
        "steps": normalized_steps,
    }


def _normalize_payout_draft(payload: dict[str, Any]) -> dict[str, Any]:
    return normalize_payout_draft(payload)


@dataclass(frozen=True)
class AiGenerationResult:
    workflow: dict[str, Any]
    source: str
    provider: str
    model: str


class BaseAiService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_workflow(self, message: str) -> AiGenerationResult:  # pragma: no cover - interface
        raise NotImplementedError

    def generate_payout_draft(self, message: str) -> AiGenerationResult:  # pragma: no cover - interface
        raise NotImplementedError


class MockAiService(BaseAiService):
    def generate_workflow(self, message: str) -> AiGenerationResult:
        return AiGenerationResult(
            workflow=interpret_request(message),
            source="mock",
            provider="mock",
            model="rule-based",
        )

    def generate_payout_draft(self, message: str) -> AiGenerationResult:
        return AiGenerationResult(
            workflow=parse_payout_draft_mock(message),
            source="mock",
            provider="mock",
            model="rule-based",
        )


class OpenAIAiService(BaseAiService):
    SYSTEM_PROMPT = (
        "You convert user workflow intents into strict JSON.\n"
        "Return JSON only with keys: workflow_name (string), business_summary (string), "
        "steps (array of {id, type, params}).\n"
        "Do not include markdown or prose."
    )
    PAYOUT_SYSTEM_PROMPT = (
        "You convert natural-language contractor payout requests into strict JSON.\n"
        "Return JSON only with keys:\n"
        "- draft_type: always contractor_payout\n"
        "- name: short workflow name\n"
        "- summary: one-sentence business summary\n"
        "- recipient_name: extracted recipient name or null\n"
        "- amount: positive number\n"
        "- asset: USDC or USDT\n"
        "- schedule_cadence: manual, weekly, or monthly\n"
        "- schedule_day: weekday for weekly, day-of-month string for monthly, or null\n"
        "Do not include markdown or prose."
    )

    def generate_workflow(self, message: str) -> AiGenerationResult:
        body = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{self.settings.openai_base_url}/chat/completions"
        with httpx.Client(timeout=self.settings.ai_timeout_seconds) as client:
            res = client.post(endpoint, headers=headers, json=body)
            res.raise_for_status()
            payload = res.json()
        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        workflow = _normalize_workflow(_extract_json_object(content))
        return AiGenerationResult(
            workflow=workflow,
            source="live",
            provider="openai",
            model=self.settings.ai_model,
        )

    def generate_payout_draft(self, message: str) -> AiGenerationResult:
        body = {
            "model": self.settings.ai_model,
            "messages": [
                {"role": "system", "content": self.PAYOUT_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        endpoint = f"{self.settings.openai_base_url}/chat/completions"
        with httpx.Client(timeout=self.settings.ai_timeout_seconds) as client:
            res = client.post(endpoint, headers=headers, json=body)
            res.raise_for_status()
            payload = res.json()
        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        draft = _normalize_payout_draft(_extract_json_object(content))
        draft["source_message"] = message.strip()
        return AiGenerationResult(
            workflow=draft,
            source="live",
            provider="openai",
            model=self.settings.ai_model,
        )


def get_ai_service(settings: Settings) -> BaseAiService:
    if settings.ai_mock_mode:
        return MockAiService(settings)
    return OpenAIAiService(settings)
