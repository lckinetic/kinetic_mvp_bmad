from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class WorkflowComponent(BaseModel):
    id: str = Field(..., description="Unique component step id")
    type: str = Field(..., description="Component name from SUPPORTED_COMPONENTS")
    params: Dict[str, Any] = Field(default_factory=dict)


class GeneratedWorkflow(BaseModel):
    workflow_name: str
    business_summary: str
    steps: List[WorkflowComponent]