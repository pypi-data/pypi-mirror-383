from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Callable, Mapping, Tuple
import math

class OneRepMaxMethod(Protocol):
    def __call__(self, weight: float, reps: int) -> float: ...

def _epley(weight: float, reps: int) -> float:
    # Epley: 1RM = w * (1 + r/30)
    return weight * (1.0 + reps / 30.0)

def _brzycki(weight: float, reps: int) -> float:
    # Brzycki: 1RM = w * 36/(37 - r)
    if reps >= 37:
        raise ValueError("Reps too high for Brzycki formula (max 36).")
    return weight * 36.0 / (37.0 - reps)

def _lombardi(weight: float, reps: int) -> float:
    # Lombardi: 1RM = w * r^0.10
    return weight * (reps ** 0.10)

def _mayhew(weight: float, reps: int) -> float:
    # Mayhew et al. (1992) bench formula
    return (100.0 * weight) / (52.2 + 41.9 * math.exp(-0.055 * reps))

_METHODS: Dict[str, OneRepMaxMethod] = {
    "epley": _epley,
    "brzycki": _brzycki,
    "lombardi": _lombardi,
    "mayhew": _mayhew,
}

def available_1rm_methods() -> Tuple[str, ...]:
    return tuple(sorted(_METHODS.keys()))

def estimate_1rm(weight: float, reps: int, method: str = "epley") -> float:
    if reps < 1:
        raise ValueError("reps must be >= 1")
    try:
        fn = _METHODS[method.lower()]
    except KeyError as e:
        raise KeyError(f"Unknown method '{method}'. Available: {available_1rm_methods()}") from e
    return fn(weight, reps)

# --- RPE / %1RM table ---
# Simplified strength community table; values are approximate anchors.
# rows: RPE 6.0 .. 10.0 (0.5 steps), cols: reps 1..12
PercentTable = Dict[float, Dict[int, float]]  # RPE -> reps -> %1RM in decimal

_BASE_TABLE: PercentTable = {
    10.0: {1:1.00, 2:0.96, 3:0.92, 4:0.89, 5:0.86, 6:0.84, 7:0.81, 8:0.79, 9:0.76, 10:0.74, 11:0.72, 12:0.70},
     9.5: {1:0.98, 2:0.94, 3:0.90, 4:0.87, 5:0.85, 6:0.82, 7:0.80, 8:0.77, 9:0.75, 10:0.73, 11:0.71, 12:0.69},
     9.0: {1:0.96, 2:0.92, 3:0.88, 4:0.86, 5:0.83, 6:0.81, 7:0.78, 8:0.76, 9:0.74, 10:0.72, 11:0.70, 12:0.68},
     8.5: {1:0.94, 2:0.90, 3:0.86, 4:0.84, 5:0.81, 6:0.79, 7:0.77, 8:0.75, 9:0.73, 10:0.71, 11:0.69, 12:0.67},
     8.0: {1:0.92, 2:0.88, 3:0.85, 4:0.82, 5:0.80, 6:0.78, 7:0.76, 8:0.74, 9:0.72, 10:0.70, 11:0.68, 12:0.66},
     7.5: {1:0.90, 2:0.87, 3:0.83, 4:0.80, 5:0.78, 6:0.76, 7:0.74, 8:0.72, 9:0.70, 10:0.68, 11:0.66, 12:0.64},
     7.0: {1:0.88, 2:0.85, 3:0.81, 4:0.79, 5:0.77, 6:0.75, 7:0.73, 8:0.71, 9:0.69, 10:0.67, 11:0.65, 12:0.63},
     6.5: {1:0.86, 2:0.83, 3:0.79, 4:0.77, 5:0.75, 6:0.73, 7:0.71, 8:0.69, 9:0.67, 10:0.65, 11:0.63, 12:0.61},
     6.0: {1:0.84, 2:0.81, 3:0.77, 4:0.75, 5:0.73, 6:0.71, 7:0.69, 8:0.67, 9:0.65, 10:0.63, 11:0.61, 12:0.59},
}

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

def rpe_to_percent(rpe: float, reps: int) -> float:
    """Return approximate %1RM (as decimal) for given RPE and reps, with bilinear interpolation."""
    reps = int(_clamp(reps, 1, 12))
    rpes = sorted(_BASE_TABLE.keys())
    rpe = _clamp(rpe, rpes[0], rpes[-1])

    # find neighbors
    lower = max([x for x in rpes if x <= rpe])
    upper = min([x for x in rpes if x >= rpe])

    if lower == upper:
        return _BASE_TABLE[lower][reps]

    # linear interpolate over RPE
    lo = _BASE_TABLE[lower][reps]
    hi = _BASE_TABLE[upper][reps]
    t = (rpe - lower) / (upper - lower)
    return lo + t * (hi - lo)

def percent_to_rpe(percent: float, reps: int) -> float:
    """Inverse lookup via search over RPE grid; returns the closest RPE."""
    reps = int(_clamp(reps, 1, 12))
    percent = _clamp(percent, 0.5, 1.0)
    best = min(_BASE_TABLE.items(), key=lambda kv: abs(kv[1][reps] - percent))
    return float(best[0])

def predict_weight_for_reps(one_rm: float, reps: int, rpe: float) -> float:
    pct = rpe_to_percent(rpe, reps)
    return one_rm * pct


# --- RIR/RPE converters ---
def rir_to_rpe(rir: float) -> float:
    """Approximate mapping used in many practical templates: RPE ≈ 10 - RIR."""
    return _clamp(10.0 - rir, 6.0, 10.0)

def rpe_to_rir(rpe: float) -> float:
    return _clamp(10.0 - rpe, 0.0, 4.0)

# --- %1RM helpers ---
def percent_load(one_rm: float, percent: float, round_to: float | None = 2.5) -> float:
    """Return absolute load for a given percent (decimal). Optionally round to plate increment."""
    percent = _clamp(percent, 0.0, 1.5)
    load = one_rm * percent
    if round_to and round_to > 0:
        return round(round(load / round_to) * round_to, 2)
    return round(load, 2)

def load_for(reps: int, rpe: float, one_rm: float, round_to: float | None = 2.5) -> float:
    """Convenience wrapper: compute planned load from reps & RPE."""
    pct = rpe_to_percent(rpe, reps)
    return percent_load(one_rm, pct, round_to=round_to)
