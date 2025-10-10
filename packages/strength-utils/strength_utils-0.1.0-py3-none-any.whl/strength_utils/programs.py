from __future__ import annotations
from typing import List, Sequence, Tuple
from .models import Exercise, SetScheme, SetPrescription, Workout, SessionPlan

def program_ppl() -> List[SessionPlan]:
    """Return a simple Push/Pull/Legs 3-day template as SessionPlans with RPE targets."""
    push = Workout(
        name="Push",
        prescriptions=[
            SetPrescription(Exercise("Bench Press", ("chest","triceps","front delts")), 5, SetScheme(reps=5, rpe=8.0)),
            SetPrescription(Exercise("Overhead Press", ("delts","triceps")), 4, SetScheme(reps=6, rpe=7.5)),
            SetPrescription(Exercise("Incline DB Press", ("chest","triceps")), 3, SetScheme(reps=10, rpe=7.0)),
        ],
    )
    pull = Workout(
        name="Pull",
        prescriptions=[
            SetPrescription(Exercise("Deadlift", ("posterior chain","back")), 3, SetScheme(reps=5, rpe=8.0)),
            SetPrescription(Exercise("Barbell Row", ("lats","upper back")), 4, SetScheme(reps=8, rpe=7.5)),
            SetPrescription(Exercise("Lat Pulldown", ("lats","biceps")), 3, SetScheme(reps=10, rpe=7.0)),
        ],
    )
    legs = Workout(
        name="Legs",
        prescriptions=[
            SetPrescription(Exercise("Back Squat", ("quads","glutes")), 5, SetScheme(reps=5, rpe=8.0)),
            SetPrescription(Exercise("Romanian Deadlift", ("hamstrings","glutes")), 3, SetScheme(reps=8, rpe=7.0)),
            SetPrescription(Exercise("Leg Press", ("quads","glutes")), 3, SetScheme(reps=12, rpe=7.0)),
        ],
    )
    return [
        SessionPlan(day="Day 1", workout=push),
        SessionPlan(day="Day 2", workout=pull),
        SessionPlan(day="Day 3", workout=legs),
    ]

def program_5x5(weeks: int = 4) -> List[SessionPlan]:
    """Generate a classic 3-day A/B 5x5 across given weeks: A and B alternate.
    A: Squat 5x5, Bench 5x5, Row 5x5
    B: Squat 5x5, Overhead Press 5x5, Deadlift 1x5 (heavy)
    RPE targets ~7.5-8.0
    """
    day_plans: List[SessionPlan] = []
    A = Workout(
        name="5x5 - A",
        prescriptions=[
            SetPrescription(Exercise("Back Squat", ("quads","glutes")), 5, SetScheme(reps=5, rpe=7.5)),
            SetPrescription(Exercise("Bench Press", ("chest","triceps")), 5, SetScheme(reps=5, rpe=7.5)),
            SetPrescription(Exercise("Barbell Row", ("lats","upper back")), 5, SetScheme(reps=5, rpe=7.5)),
        ],
    )
    B = Workout(
        name="5x5 - B",
        prescriptions=[
            SetPrescription(Exercise("Back Squat", ("quads","glutes")), 5, SetScheme(reps=5, rpe=8.0)),
            SetPrescription(Exercise("Overhead Press", ("delts","triceps")), 5, SetScheme(reps=5, rpe=7.5)),
            SetPrescription(Exercise("Deadlift", ("posterior chain","back")), 1, SetScheme(reps=5, rpe=8.0)),
        ],
    )
    days = ["Day 1", "Day 2", "Day 3"]
    for w in range(weeks):
        # Alternate starting workout each week for balanced exposure
        if w % 2 == 0:
            wkouts = [A, B, A]
        else:
            wkouts = [B, A, B]
        for d, wk in zip(days, wkouts):
            day_plans.append(SessionPlan(day=f"Week {w+1} - {d}", workout=wk))
    return day_plans
