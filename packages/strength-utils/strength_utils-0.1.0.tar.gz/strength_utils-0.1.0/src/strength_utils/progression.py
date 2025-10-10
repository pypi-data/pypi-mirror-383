from __future__ import annotations
from typing import List, Tuple

def linear_progression(current_weight: float, increment: float, weeks: int) -> List[float]:
    return [current_weight + i * increment for i in range(weeks)]

def double_progression(
    base_weight: float, reps_range: Tuple[int, int], sets: int, target_sets: int, rep_increment: int = 1
) -> List[Tuple[int, int, float]]:
    """Return a sequence of (sets, reps, weight). Increase reps until top of range then add weight and reset reps."""
    lo, hi = reps_range
    if lo > hi: raise ValueError("reps_range must be (lo, hi)")
    scheme: List[Tuple[int, int, float]] = []
    weight = base_weight
    sets_done = sets
    reps = lo
    for _ in range(20):
        scheme.append((sets_done, reps, weight))
        reps += rep_increment
        if reps > hi:
            reps = lo
            weight = round(weight + 2.5, 2)
            if sets_done < target_sets:
                sets_done += 1
    return scheme

def rir_progression(start_weight: float, weeks: int, weekly_delta: float = 2.5) -> List[float]:
    return [round(start_weight + i * weekly_delta, 2) for i in range(weeks)]
