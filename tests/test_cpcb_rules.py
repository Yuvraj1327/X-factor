"""
tests/test_cpcb_rules.py
─────────────────────────
Tests for CPCB threshold logic and risk scoring.
"""
from __future__ import annotations

import pytest

from app.analysis.cpcb_rules import get_default_thresholds
from app.analysis.engine import rank_ghats, _risk_score, _assess_parameter


class TestCPCBThresholds:
    def test_dissolved_oxygen_below_limit(self):
        thresholds = get_default_thresholds()
        t = thresholds["dissolved_oxygen"]
        assert t.exceeds(4.9) is True  # Below minimum 5.0

    def test_dissolved_oxygen_at_limit(self):
        thresholds = get_default_thresholds()
        t = thresholds["dissolved_oxygen"]
        assert t.exceeds(5.0) is False

    def test_bod_above_limit(self):
        thresholds = get_default_thresholds()
        t = thresholds["bod"]
        assert t.exceeds(3.1) is True  # Above max 3.0

    def test_bod_within_limit(self):
        thresholds = get_default_thresholds()
        t = thresholds["bod"]
        assert t.exceeds(2.5) is False

    def test_ph_below_range(self):
        thresholds = get_default_thresholds()
        t = thresholds["ph"]
        assert t.exceeds(6.4) is True

    def test_ph_above_range(self):
        thresholds = get_default_thresholds()
        t = thresholds["ph"]
        assert t.exceeds(8.6) is True

    def test_ph_within_range(self):
        thresholds = get_default_thresholds()
        t = thresholds["ph"]
        assert t.exceeds(7.5) is False

    def test_fecal_coliform_above_limit(self):
        thresholds = get_default_thresholds()
        t = thresholds["fecal_coliform"]
        assert t.exceeds(501) is True

    def test_all_defaults_present(self):
        thresholds = get_default_thresholds()
        expected = {"dissolved_oxygen", "bod", "ph", "fecal_coliform", "total_coliform", "nitrate", "turbidity"}
        assert expected.issubset(thresholds.keys())


class TestRiskScoring:
    def test_missing_data_is_not_zero(self):
        """Missing parameters contribute a precautionary penalty, not zero."""
        from app.schemas.analysis import ParameterStatus
        evidence = [
            ParameterStatus(
                parameter="dissolved_oxygen", value=None, unit="mg/L",
                cpcb_min=5.0, cpcb_max=None, water_class="B",
                exceeds_limit=None, missing=True,
            )
        ]
        score = _risk_score(evidence)
        assert score > 0, "Missing data must contribute a non-zero precautionary score"

    def test_exceeding_limit_gives_full_score(self):
        from app.schemas.analysis import ParameterStatus
        evidence = [
            ParameterStatus(
                parameter="bod", value=10.0, unit="mg/L",
                cpcb_min=None, cpcb_max=3.0, water_class="B",
                exceeds_limit=True, missing=False,
            )
        ]
        score = _risk_score(evidence)
        assert score == 100.0

    def test_within_limit_gives_zero_score(self):
        from app.schemas.analysis import ParameterStatus
        evidence = [
            ParameterStatus(
                parameter="ph", value=7.0, unit="",
                cpcb_min=6.5, cpcb_max=8.5, water_class="B",
                exceeds_limit=False, missing=False,
            )
        ]
        score = _risk_score(evidence)
        assert score == 0.0


class TestGhatRanking:
    def test_ghat_with_bad_data_ranks_first(self):
        ghats_data = [
            {
                "ghat_id": 1, "ghat_name": "Clean Ghat", "ghat_slug": "clean-ghat",
                "latest_reading": {
                    "sampling_date": None, "dissolved_oxygen": 7.0,
                    "bod": 1.0, "ph": 7.5, "fecal_coliform": 100,
                    "total_coliform": 500, "nitrate": 10, "turbidity": 5,
                },
            },
            {
                "ghat_id": 2, "ghat_name": "Polluted Ghat", "ghat_slug": "polluted-ghat",
                "latest_reading": {
                    "sampling_date": None, "dissolved_oxygen": 2.0,  # Very low
                    "bod": 15.0,  # Very high
                    "ph": 9.5, "fecal_coliform": 2000, "total_coliform": 10000,
                    "nitrate": 60, "turbidity": 50,
                },
            },
        ]
        rankings = rank_ghats(ghats_data)
        assert rankings[0].ghat_id == 2, "Polluted ghat should be rank 1"

    def test_no_data_ghat_gets_moderate_score(self):
        ghats_data = [
            {"ghat_id": 1, "ghat_name": "Unknown Ghat", "ghat_slug": "unknown", "latest_reading": None}
        ]
        rankings = rank_ghats(ghats_data)
        assert rankings[0].risk_label == "INSUFFICIENT_DATA"

    def test_disclaimer_always_present(self):
        ghats_data = [
            {"ghat_id": 1, "ghat_name": "Test Ghat", "ghat_slug": "test", "latest_reading": None}
        ]
        rankings = rank_ghats(ghats_data)
        assert "not" in rankings[0].data_disclaimer.lower()

    def test_rankings_sorted_by_score(self):
        from datetime import datetime, timezone
        now = datetime(2020, 1, 1, tzinfo=timezone.utc)  # Old date — stale data
        ghats_data = [
            {
                "ghat_id": i, "ghat_name": f"Ghat {i}", "ghat_slug": f"ghat-{i}",
                "latest_reading": {
                    "sampling_date": now, "dissolved_oxygen": float(i),
                    "bod": None, "ph": None, "fecal_coliform": None,
                    "total_coliform": None, "nitrate": None, "turbidity": None,
                },
            }
            for i in range(1, 5)
        ]
        rankings = rank_ghats(ghats_data)
        scores = [r.risk_score for r in rankings]
        assert scores == sorted(scores, reverse=True)
