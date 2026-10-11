"""
app/analysis/cpcb_rules.py
───────────────────────────
CPCB Class B (bathing/outdoor contact) water-quality benchmark thresholds.
These are the default values used when the DB table is empty.
Source: CPCB General Standards for Discharge of Environmental Pollutants,
        and IS 2296:1982 / CPCB Designated Best Use Classification.

IMPORTANT:
  - These are reference benchmarks, not official current criteria.
  - Always check the DB (cpcb_thresholds table) for admin-configured values first.
  - Missing data is NEVER assumed to be within limits.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Threshold:
    parameter: str
    water_class: str
    min_value: Optional[float]   # None = no lower bound
    max_value: Optional[float]   # None = no upper bound
    unit: str
    description: str

    def exceeds(self, value: float) -> bool:
        """Return True if the measured value violates this threshold."""
        if self.min_value is not None and value < self.min_value:
            return True
        if self.max_value is not None and value > self.max_value:
            return True
        return False


# ── CPCB Class B defaults ─────────────────────────────────────────────────────
# Source: CPCB "Designated Best Use" classification table (Annexure I, IS 2296:1982)
# Class B: Outdoor bathing (organised).
DEFAULT_CPCB_CLASS_B: Dict[str, Threshold] = {
    "dissolved_oxygen": Threshold(
        parameter="dissolved_oxygen",
        water_class="B",
        min_value=5.0,      # ≥ 5 mg/L
        max_value=None,
        unit="mg/L",
        description="Dissolved Oxygen must be ≥ 5 mg/L for Class B (bathing)",
    ),
    "bod": Threshold(
        parameter="bod",
        water_class="B",
        min_value=None,
        max_value=3.0,      # ≤ 3 mg/L
        unit="mg/L",
        description="Biochemical Oxygen Demand must be ≤ 3 mg/L for Class B",
    ),
    "ph": Threshold(
        parameter="ph",
        water_class="B",
        min_value=6.5,
        max_value=8.5,
        unit="",
        description="pH must be between 6.5 and 8.5 for Class B",
    ),
    "fecal_coliform": Threshold(
        parameter="fecal_coliform",
        water_class="B",
        min_value=None,
        max_value=500.0,    # ≤ 500 MPN/100mL
        unit="MPN/100mL",
        description="Fecal Coliform must be ≤ 500 MPN/100mL for Class B",
    ),
    "total_coliform": Threshold(
        parameter="total_coliform",
        water_class="B",
        min_value=None,
        max_value=5000.0,   # ≤ 5000 MPN/100mL
        unit="MPN/100mL",
        description="Total Coliform must be ≤ 5000 MPN/100mL for Class B",
    ),
    "nitrate": Threshold(
        parameter="nitrate",
        water_class="B",
        min_value=None,
        max_value=45.0,     # ≤ 45 mg/L (WHO drinking-water guideline used as proxy)
        unit="mg/L",
        description="Nitrate ≤ 45 mg/L (reference: WHO guideline, used as proxy)",
    ),
    "turbidity": Threshold(
        parameter="turbidity",
        water_class="B",
        min_value=None,
        max_value=10.0,     # ≤ 10 NTU (WHO drinking-water guideline proxy)
        unit="NTU",
        description="Turbidity ≤ 10 NTU (WHO proxy; bathing contact concern)",
    ),
}


def get_default_thresholds() -> Dict[str, Threshold]:
    """Return a copy of the default CPCB Class B thresholds."""
    return dict(DEFAULT_CPCB_CLASS_B)
