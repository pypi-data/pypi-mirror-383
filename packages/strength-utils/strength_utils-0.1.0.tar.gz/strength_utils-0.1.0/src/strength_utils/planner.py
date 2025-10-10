from __future__ import annotations
from dataclasses import asdict
from typing import Iterable, Dict, List, Tuple
import csv 
import json
from .models import SetPrescription, Workout, SessionPlan
from .formulas import load_for, rpe_to_percent, percent_load

def plan_prescription_loads(
    presc: SetPrescription,
    one_rm_lookup: Dict[str, float],
    round_to: float = 2.5
) -> float:
    """Return planned absolute load for a single prescription using either fixed load or RPE-based calc.
    - If presc.scheme.load is set, use it directly.
    - Else, require one_rm_lookup[exercise.name] and presc.scheme.rpe.
    """
    if presc.scheme.load is not None:
        return float(presc.scheme.load)
    name = presc.exercise.name
    if presc.scheme.rpe is None:
        raise ValueError(f"Prescription for {name} missing 'load' and 'rpe'. Provide one.")
    if name not in one_rm_lookup:
        raise KeyError(f"Missing 1RM for exercise '{name}'.")
    return load_for(reps=presc.scheme.reps, rpe=presc.scheme.rpe, one_rm=one_rm_lookup[name], round_to=round_to)

def plan_workout(
    workout: Workout,
    one_rm_lookup: Dict[str, float],
    round_to: float = 2.5
) -> Dict[str, Dict[str, float]]:
    """Return mapping exercise -> {load, reps, sets, volume} for a Workout."""
    out: Dict[str, Dict[str, float]] = {}
    for p in workout.prescriptions:
        load = plan_prescription_loads(p, one_rm_lookup, round_to=round_to)
        vol = float(load * p.scheme.reps * p.sets)
        out[p.exercise.name] = {
            "load": round(load, 2),
            "reps": float(p.scheme.reps),
            "sets": float(p.sets),
            "volume": round(vol, 2),
        }
    return out

def export_workout_csv(path: str, plan: Dict[str, Dict[str, float]]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["exercise", "load", "reps", "sets", "volume"])
        w.writeheader()
        for ex, vals in plan.items():
            row = {"exercise": ex}
            row.update(vals)
            w.writerow(row)

def export_workout_json(path: str, plan: Dict[str, Dict[str, float]]) -> None:
    with open(path, "w") as f:
        json.dump(plan, f, indent=2, sort_keys=True)

def export_session_json(path: str, session: SessionPlan, plan: Dict[str, Dict[str, float]]) -> None:
    payload = {
        "day": session.day,
        "workout": session.workout.name,
        "plan": plan,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
