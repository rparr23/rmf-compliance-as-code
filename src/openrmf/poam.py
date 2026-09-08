"""POA&M validation and reporting."""

from datetime import UTC, date, datetime

RANK = {"low": 1, "moderate": 2, "high": 3, "critical": 4}


def _as_date(value: object) -> date:
    """Accept ISO strings and date objects produced by YAML parsers."""
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def validate_poam(data: dict, today: date | None = None) -> list[dict]:
    today = today or datetime.now(UTC).date()
    findings = []
    seen = set()
    for index, item in enumerate(data.get("items", [])):
        item_id = item.get("id", f"item-{index + 1}")
        if item_id in seen:
            findings.append({"severity": "error", "item": item_id, "message": "Duplicate ID"})
        seen.add(item_id)
        for field in ("title", "owner", "status", "planned_completion"):
            if not item.get(field):
                findings.append(
                    {"severity": "error", "item": item_id, "message": f"Missing {field}"}
                )
        if item.get("risk", {}).get("rating") not in RANK:
            findings.append(
                {"severity": "error", "item": item_id, "message": "Invalid risk rating"}
            )
        try:
            due = _as_date(item["planned_completion"])
            if due < today and item.get("status") not in {"completed", "closed"}:
                findings.append({"severity": "warning", "item": item_id, "message": "Past due"})
        except (KeyError, TypeError, ValueError):
            if item.get("planned_completion"):
                findings.append(
                    {"severity": "error", "item": item_id, "message": "Invalid completion date"}
                )
        if item.get("status") in {"completed", "closed"} and not item.get("evidence"):
            findings.append(
                {"severity": "error", "item": item_id, "message": "Closed without evidence"}
            )
    return findings


def summarize_poam(data: dict, today: date | None = None) -> dict:
    today = today or datetime.now(UTC).date()
    items = data.get("items", [])
    overdue = 0
    for item in items:
        try:
            overdue += _as_date(item["planned_completion"]) < today and item.get(
                "status"
            ) not in {"completed", "closed"}
        except (KeyError, TypeError, ValueError):
            pass
    return {
        "total": len(items),
        "open": sum(i.get("status") not in {"completed", "closed"} for i in items),
        "overdue": int(overdue),
        "critical_high": sum(
            i.get("risk", {}).get("rating") in {"critical", "high"} for i in items
        ),
    }
