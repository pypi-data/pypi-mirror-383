from __future__ import annotations
from typing import Final

KG_TO_LB: Final[float] = 2.2046226218

def kg_to_lb(kg: float) -> float:
    return kg * KG_TO_LB

def lb_to_kg(lb: float) -> float:
    return lb / KG_TO_LB
