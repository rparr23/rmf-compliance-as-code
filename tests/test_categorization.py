import pytest

from openrmf.categorization import categorize


def test_high_water_mark_selects_moderate():
    result = categorize("moderate", "low", "low")
    assert result["recommended_baseline"] == "moderate"
    assert result["requires_human_approval"] is True


def test_invalid_rating_fails():
    with pytest.raises(ValueError):
        categorize("medium", "low", "low")
