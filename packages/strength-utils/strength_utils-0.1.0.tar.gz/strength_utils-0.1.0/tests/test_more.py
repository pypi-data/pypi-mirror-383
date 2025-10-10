from strength_utils import rir_to_rpe, rpe_to_rir, percent_load, load_for, plan_workout
from strength_utils import Exercise, SetScheme, SetPrescription, Workout

def test_rir_rpe_converters():
    assert rir_to_rpe(0.0) == 10.0
    assert rpe_to_rir(10.0) == 0.0
    assert 6.0 <= rir_to_rpe(4.0) <= 10.0

def test_percent_and_load_for():
    one_rm = 200.0
    p = percent_load(one_rm, 0.8, round_to=2.5)
    assert p in (160.0, 160.0)  # rounded to 2.5
    l = load_for(reps=5, rpe=8.5, one_rm=one_rm, round_to=2.5)
    assert l > 0.0

def test_plan_workout():
    squat = Exercise("Back Squat", ("quads","glutes"))
    scheme = SetScheme(reps=5, rpe=8.0)
    presc = SetPrescription(exercise=squat, sets=5, scheme=scheme)
    wk = Workout(name="Day 1", prescriptions=[presc])
    plan = plan_workout(wk, {"Back Squat": 180.0}, round_to=2.5)
    assert "Back Squat" in plan
    assert plan["Back Squat"]["load"] > 0
