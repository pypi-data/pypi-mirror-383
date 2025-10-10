# strength-utils

Please note that this package is undergoing regular changes. 

Typed utilities for strength training and programming.

## Features
- Multiple 1RM estimation formulas (Epley, Brzycki, Lombardi, Mayhew).
- Predict training weight at target reps or RPE.
- RPE ↔ %1RM tables (with interpolation).
- Volume/tonnage calculations per exercise and per session.
- Basic progression helpers (linear, double progression, RIR-based).
- Simple templated programs (e.g., 5x5, PPL) as typed data models.
- Unit conversion utilities (kg/lb).
- 100% type-hinted code.

## Quickstart

```python
from strength_utils import estimate_1rm, predict_weight_for_reps, rpe_to_percent

one_rm = estimate_1rm(weight=140.0, reps=5, method="epley")  # ~163.3 kg
target = predict_weight_for_reps(one_rm, reps=3, rpe=9.0)    # planned training weight
print(one_rm, target)
```

## License
MIT


## Percent tables per lift

```python
from strength_utils import make_percent_table_by_lift
tables = make_percent_table_by_lift({"Back Squat": 180.0, "Bench Press": 120.0})
print(tables["Back Squat"][0.8])  # -> 1RM * 0.8 rounded to nearest 2.5 kg
```

## Program generators (PPL & 5x5)

```python
from strength_utils import program_ppl, program_5x5
ppl = program_ppl()            # 3-day template
five = program_5x5(weeks=4)    # 12 sessions (3 per week)
for s in ppl:
    print(s.day, s.workout.name, len(s.workout.prescriptions))
```
