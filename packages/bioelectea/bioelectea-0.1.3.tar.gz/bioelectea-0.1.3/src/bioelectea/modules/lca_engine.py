"""LCA engine scaffold for BioElecTEA."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class LCAItem:
    name: str
    amount: float  # e.g., kg, kWh
    gwp_factor: float  # kg CO2e per unit
    ce_factor: float  # placeholder score per unit


@dataclass
class LCAResult:
    total_gwp: float
    total_ce: float
    breakdown: List[Tuple[str, float, float]]  # (name, gwp, ce)


class LCAEngine:
    def __init__(self, items: List[LCAItem]) -> None:
        self.items = items

    def evaluate(self) -> LCAResult:
        breakdown: List[Tuple[str, float, float]] = []
        gwp_sum = 0.0
        ce_sum = 0.0
        for it in self.items:
            gwp = it.amount * it.gwp_factor
            ce = it.amount * it.ce_factor
            breakdown.append((it.name, gwp, ce))
            gwp_sum += gwp
            ce_sum += ce
        breakdown.sort(key=lambda x: x[1], reverse=True)
        return LCAResult(total_gwp=gwp_sum, total_ce=ce_sum, breakdown=breakdown)
