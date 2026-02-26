from typing import Any, Dict
from fastapi import HTTPException


def validate_template_input(input_data: Dict[str, Any], schema: list[dict]) -> Dict[str, Any]:
    validated: Dict[str, Any] = {}

    for field in schema:
        name = field["name"]
        field_type = field.get("type", "string")
        required = field.get("required", False)

        value = input_data.get(name, field.get("default"))

        # Required check
        if required and value is None:
            raise HTTPException(status_code=400, detail=f"Field '{name}' is required")

        if value is None:
            continue

        # Type handling
        if field_type == "number":
            try:
                value = float(value)
            except Exception:
                raise HTTPException(status_code=400, detail=f"Field '{name}' must be a number")

            if "min" in field and value < field["min"]:
                raise HTTPException(status_code=400, detail=f"Field '{name}' must be >= {field['min']}")

        elif field_type == "select":
            options = field.get("options", [])
            if value not in options:
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{name}' must be one of {options}",
                )

        elif field_type == "email":
            if "@" not in value:
                raise HTTPException(status_code=400, detail=f"Field '{name}' must be a valid email")

        validated[name] = value

    return validated