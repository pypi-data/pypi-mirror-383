from __future__ import annotations
from typing import Dict, Tuple
from .models import SetPrescription

def set_volume(weight: float, reps: int, sets: int) -> float:
    """Tonnage (kg) for a given prescription."""
    return weight * reps * sets

def total_tonnage(prescriptions: Tuple[SetPrescription, ...], weights: Dict[str, float]) -> float:
    """Sum tonnage over prescriptions; weights maps exercise name -> planned load."""
    ton = 0.0
    for p in prescriptions:
        w = weights.get(p.exercise.name, 0.0)
        ton += set_volume(w, p.scheme.reps, p.sets)
    return ton

def workout_volume(prescriptions: Tuple[SetPrescription, ...], weights: Dict[str, float]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for p in prescriptions:
        w = weights.get(p.exercise.name, 0.0)
        out[p.exercise.name] = out.get(p.exercise.name, 0.0) + set_volume(w, p.scheme.reps, p.sets)
    return out
