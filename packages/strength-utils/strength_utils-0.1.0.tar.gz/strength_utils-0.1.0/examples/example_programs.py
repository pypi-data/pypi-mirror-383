from strength_utils import program_ppl, program_5x5, make_percent_table_by_lift, plan_workout

def main() -> None:
    ppl = program_ppl()
    five = program_5x5(weeks=2)
    one_rms = {"Back Squat": 180.0, "Bench Press": 120.0, "Deadlift": 220.0, "Overhead Press": 80.0,"Incline DB Press": 60.0,"Barbell Row": 100.0,"Lat Pulldown": 90.0,"Romanian Deadlift": 140.0,"Leg Press": 200.0}
    tables = make_percent_table_by_lift(one_rms)

    # Plan the first session in each program
    p1 = plan_workout(ppl[0].workout, one_rms)
    p2 = plan_workout(five[0].workout, one_rms)

    print("PPL Day 1 plan:", p1)
    print()
    print("5x5 W1D1 plan:", p2)
    print()
    print("80% squat load:", tables["Back Squat"][0.8])

if __name__ == "__main__":
    main()
