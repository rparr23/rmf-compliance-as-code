from datetime import date

from openrmf.poam import validate_poam
from openrmf.validator import validate_system


def test_closed_poam_requires_evidence():
    data = {
        "items": [
            {
                "id": "P-1",
                "title": "x",
                "owner": "a",
                "status": "closed",
                "planned_completion": "2026-01-01",
                "risk": {"rating": "low"},
                "evidence": [],
            }
        ]
    }
    assert any("without evidence" in x["message"] for x in validate_poam(data, date(2026, 2, 1)))


def test_placeholder_fails():
    data = {
        "system": {"name": "x", "owner": "y", "authorization_boundary": "z"},
        "categorization": {"confidentiality": "low", "integrity": "low", "availability": "low"},
        "controls": [
            {
                "id": "AC-2",
                "status": "implemented",
                "implementation_statement": "TBD after the security team completes its review.",
            }
        ],
    }
    assert any(x["severity"] == "error" for x in validate_system(data))
