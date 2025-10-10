from strength_utils import (
    Exercise, SetScheme, SetPrescription, Workout, SessionPlan,
    plan_workout, export_workout_csv, export_workout_json, export_session_json
)
import os

def main() -> None:
    squat = Exercise("Back Squat", ("quads","glutes"))
    scheme = SetScheme(reps=5, rpe=7.5)
    presc = SetPrescription(exercise=squat, sets=5, scheme=scheme)
    wk = Workout(name="Day 1", prescriptions=[presc])
    session = SessionPlan(day="Monday", workout=wk)
    one_rms = {"Back Squat": 180.0}
    cwd = os.path.dirname(os.path.abspath(__file__))
    plan = plan_workout(wk, one_rms, round_to=2.5)
    export_workout_csv(os.path.join(cwd, "example_output/workout.csv"), plan)
    export_workout_json(os.path.join(cwd, "example_output/workout.json"), plan)
    export_session_json(os.path.join(cwd, "example_output/session.json"), session, plan)

if __name__ == "__main__":
    main()
