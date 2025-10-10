import streamlit as st
from typing import Dict
from strength_utils import (
    Exercise, SetScheme, SetPrescription, Workout,
    estimate_1rm, plan_workout, export_workout_csv, export_workout_json,
    load_for, rpe_to_percent
)

st.set_page_config(page_title="Strength Planner", layout="centered")
st.title("Strength Planner (typed utilities)")

st.sidebar.header("1RM Inputs")
one_rms: Dict[str, float] = {}
for ex in ["Back Squat", "Bench Press", "Deadlift", "Overhead Press"]:
    one_rms[ex] = st.sidebar.number_input(f"{ex} 1RM (kg)", min_value=0.0, value=100.0 if ex != "Deadlift" else 140.0, step=2.5)

st.header("Workout Builder")
name = st.text_input("Workout name", "Day 1")
ex_name = st.selectbox("Exercise", list(one_rms.keys()))
reps = st.number_input("Reps", min_value=1, max_value=20, value=5, step=1)
sets = st.number_input("Sets", min_value=1, max_value=10, value=5, step=1)
rpe = st.slider("RPE", min_value=6.0, max_value=10.0, value=7.5, step=0.5)

round_to = st.selectbox("Plate increment (kg)", [None, 0.5, 1.0, 1.25, 2.5, 5.0], index=5)

ex = Exercise(ex_name, ())
scheme = SetScheme(reps=int(reps), rpe=float(rpe))
presc = SetPrescription(exercise=ex, sets=int(sets), scheme=scheme)
wk = Workout(name=name, prescriptions=[presc])

if st.button("Plan workout"):
    plan = plan_workout(wk, one_rms, round_to=2.5 if round_to is None else float(round_to))
    st.subheader("Planned Loads")
    st.table([{ "exercise": k, **v } for k, v in plan.items()])

    col1, col2 = st.columns(2)
    with col1:
        if st.download_button("Download CSV", data="exercise,load,reps,sets,volume\n" + "\n".join(
            f"{k},{v['load']},{int(v['reps'])},{int(v['sets'])},{v['volume']}" for k,v in plan.items()
        ), file_name="workout.csv", mime="text/csv"):
            pass
    with col2:
        import json
        if st.download_button("Download JSON", data=json.dumps(plan, indent=2), file_name="workout.json", mime="application/json"):
            pass

st.caption("Tip: Change 1RMs, reps, and RPE to see updated planned loads. Uses RPE→%1RM interpolation.")
