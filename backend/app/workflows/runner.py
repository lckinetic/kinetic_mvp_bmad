from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import Settings
from app.services.banxa_client import BanxaClient
from app.workflows.registry import get_template
from app.workflows.validation import validate_template_input


def run_template(
    *,
    db: Session,
    settings: Settings,
    template_name: str,
    run_input: Dict[str, Any],
) -> Dict[str, Any]:
    # Validate template exists
    try:
        t = get_template(template_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Template not found")

    schema = t.get("input_schema", [])
    validated_input = validate_template_input(run_input, schema)

    # Ensure run_id survives validation (your validator may drop unknown keys)
    if "run_id" in run_input:
        validated_input["run_id"] = run_input["run_id"]

    banxa = BanxaClient(mock_mode=settings.mock_mode)

    fn = t["function"]
    return fn(db=db, settings=settings, banxa=banxa, input=validated_input) or {}