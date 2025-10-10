from strength_utils import make_percent_table, make_percent_table_by_lift, program_ppl, program_5x5

def test_percent_table_ranges():
    tbl = make_percent_table(200.0)
    assert 0.5 in tbl and 1.0 in tbl  # has 50% and 100%
    assert tbl[1.0] == 200.0  # rounded to 2.5 should still be 200

def test_percent_table_by_lift():
    tables = make_percent_table_by_lift({"Back Squat": 180.0, "Bench Press": 120.0})
    assert "Back Squat" in tables and 0.8 in tables["Back Squat"]

def test_program_generators_shape():
    ppl = program_ppl()
    assert len(ppl) == 3
    five = program_5x5(weeks=3)
    assert len(five) == 9
