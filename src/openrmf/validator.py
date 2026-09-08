"""Cross-artifact validation rules."""

import re

CONTROL_ID = re.compile(r"^[A-Z]{2,3}-\d+(?:\(\d+\))?$")
PLACEHOLDERS = ("TBD", "TODO", "INSERT HERE", "UNKNOWN", "XX/XX/XXXX", "Lorem ipsum")


def validate_system(data: dict) -> list[dict]:
    findings = []
    for path in ("system.name", "system.owner", "system.authorization_boundary"):
        value = data
        for key in path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if not value:
            findings.append(
                {"severity": "error", "field": path, "message": "Required field is missing"}
            )
    impacts = data.get("categorization", {})
    for dimension in ("confidentiality", "integrity", "availability"):
        if impacts.get(dimension) not in {"low", "moderate", "high"}:
            findings.append(
                {
                    "severity": "error",
                    "field": f"categorization.{dimension}",
                    "message": "Use low, moderate, or high",
                }
            )
    for control in data.get("controls", []):
        control_id = control.get("id", "")
        if not CONTROL_ID.match(control_id):
            findings.append(
                {
                    "severity": "error",
                    "field": "controls.id",
                    "message": f"Invalid control ID: {control_id}",
                }
            )
        statement = control.get("implementation_statement", "")
        if any(token.lower() in statement.lower() for token in PLACEHOLDERS):
            findings.append(
                {
                    "severity": "error",
                    "field": control_id,
                    "message": "Implementation statement contains a placeholder",
                }
            )
        if len(statement.strip()) < 40:
            findings.append(
                {
                    "severity": "warning",
                    "field": control_id,
                    "message": "Implementation statement may lack sufficient detail",
                }
            )
        if control.get("status") == "not-applicable" and not control.get("tailoring_rationale"):
            findings.append(
                {
                    "severity": "error",
                    "field": control_id,
                    "message": "Not-applicable control requires rationale",
                }
            )
    return findings
