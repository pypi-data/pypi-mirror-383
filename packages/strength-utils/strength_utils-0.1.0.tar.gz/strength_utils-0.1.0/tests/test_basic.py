import math
from strength_utils import estimate_1rm, rpe_to_percent, percent_to_rpe, kg_to_lb, lb_to_kg

def test_1rm_methods():
    e = estimate_1rm(100, 5, "epley")
    b = estimate_1rm(100, 5, "brzycki")
    assert e > b  # epley tends to estimate slightly higher than brzycki at 5 reps

def test_rpe_percent_roundtrip():
    p = rpe_to_percent(9.0, 5)
    r = percent_to_rpe(p, 5)
    assert 8.5 <= r <= 9.5

def test_units():
    kg = 100.0
    lb = kg_to_lb(kg)
    assert math.isclose(lb_to_kg(lb), kg, rel_tol=1e-9)
