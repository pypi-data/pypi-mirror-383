"""TEA core calculations for BioElecTEA."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TEAInput:
    years: int
    discount_rate: float  # e.g., 0.08
    capex: float  # upfront
    opex_yearly: float  # constant v0
    revenue_yearly: float  # constant v0


@dataclass
class TEAResult:
    npv: float
    irr: Optional[float]
    payback_year: Optional[int]
    cashflows: List[float]


class TEACore:
    def __init__(self, params: TEAInput) -> None:
        self.p = params

    def build_cashflows(self) -> List[float]:
        cf: List[float] = [-self.p.capex]
        for _ in range(self.p.years):
            cf.append(self.p.revenue_yearly - self.p.opex_yearly)
        return cf

    @staticmethod
    def npv(rate: float, cashflows: List[float]) -> float:
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))

    @staticmethod
    def irr(
        cashflows: List[float],
        guess: float = 0.1,
        tol: float = 1e-6,
        max_iter: int = 100,
    ) -> Optional[float]:
        # Simple Newton-Raphson (demo). For production consider numpy_financial.
        rate = guess
        for _ in range(max_iter):
            f = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))
            df = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cashflows) if t > 0)
            if abs(df) < 1e-12:
                return None
            new_rate = rate - f / df
            if abs(new_rate - rate) < tol:
                return new_rate
            rate = new_rate
        return None

    @staticmethod
    def payback(cashflows: List[float]) -> Optional[int]:
        acc = 0.0
        for t, cf in enumerate(cashflows):
            acc += cf
            if acc >= 0:
                return t
        return None

    def run(self) -> TEAResult:
        cfs = self.build_cashflows()
        npv_val = self.npv(self.p.discount_rate, cfs)
        irr_val = self.irr(cfs)
        pby = self.payback(cfs)
        return TEAResult(npv=npv_val, irr=irr_val, payback_year=pby, cashflows=cfs)
