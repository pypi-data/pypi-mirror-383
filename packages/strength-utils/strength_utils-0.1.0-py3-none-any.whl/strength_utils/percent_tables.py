from __future__ import annotations
from typing import Dict, Iterable, List, Tuple
from .formulas import percent_load

def make_percent_table(
    one_rm: float,
    percents: Iterable[float] | None = None,
    round_to: float | None = 2.5
) -> Dict[float, float]:
    """Return a mapping of percent (decimal) -> planned load for a given 1RM.
    Defaults to 50%..105% in 0.025 (2.5%) steps.
    """
    if percents is None:
        percents = [x/100 for x in range(50, 106, 2)]  # 50,52,54,...,104
    table: Dict[float, float] = {}
    for p in percents:
        table[round(p, 4)] = percent_load(one_rm, p, round_to=round_to)
    return dict(sorted(table.items()))

def make_percent_table_by_lift(
    one_rms: Dict[str, float],
    percents: Iterable[float] | None = None,
    round_to: float | None = 2.5
) -> Dict[str, Dict[float, float]]:
    """Return nested mapping lift -> {percent->load}."""
    return { lift: make_percent_table(orm, percents=percents, round_to=round_to) for lift, orm in one_rms.items() }
