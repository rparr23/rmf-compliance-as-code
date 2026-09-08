"""FIPS 199 decision-support categorization."""

LEVELS = {"low": 1, "moderate": 2, "high": 3}


def categorize(confidentiality: str, integrity: str, availability: str) -> dict:
    ratings = {
        "confidentiality": confidentiality.lower(),
        "integrity": integrity.lower(),
        "availability": availability.lower(),
    }
    invalid = [name for name, value in ratings.items() if value not in LEVELS]
    if invalid:
        raise ValueError(f"Invalid impact rating for: {', '.join(invalid)}")
    overall = max(ratings.values(), key=LEVELS.get)
    return {
        "ratings": ratings,
        "overall": overall,
        "recommended_baseline": overall,
        "requires_human_approval": True,
        "method": "FIPS 199 high-water mark",
    }
