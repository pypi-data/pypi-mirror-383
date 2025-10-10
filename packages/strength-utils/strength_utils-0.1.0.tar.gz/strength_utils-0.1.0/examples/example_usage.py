from strength_utils import estimate_1rm, predict_weight_for_reps, rpe_to_percent, linear_progression

def main() -> None:
    one_rm = estimate_1rm(140.0, 5, method="epley")
    planned = predict_weight_for_reps(one_rm, reps=3, rpe=9.0)
    pct = rpe_to_percent(8.5, 6)
    plan = linear_progression(current_weight=100.0, increment=2.5, weeks=12)
    print(f"1RM≈{one_rm:.1f} kg, triple@9 ≈ {planned:.1f} kg, 6@8.5 ≈ {pct*100:.0f}% 1RM")
    print("Linear plan:", plan)

if __name__ == "__main__":
    main()
