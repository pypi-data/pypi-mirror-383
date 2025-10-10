from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

MuscleGroup = str

@dataclass(frozen=True, slots=True)
class Exercise:
    name: str
    muscle_groups: Tuple[MuscleGroup, ...] = ("full body",)

@dataclass(frozen=True, slots=True)
class SetScheme:
    reps: int
    rpe: Optional[float] = None
    load: Optional[float] = None  # absolute weight if fixed
    rir: Optional[float] = None

@dataclass(frozen=True, slots=True)
class SetPrescription:
    exercise: Exercise
    sets: int
    scheme: SetScheme

@dataclass(slots=True)
class Workout:
    name: str
    prescriptions: List[SetPrescription] = field(default_factory=list)

    def add(self, presc: SetPrescription) -> None:
        self.prescriptions.append(presc)

@dataclass(slots=True)
class SessionPlan:
    day: str
    workout: Workout
