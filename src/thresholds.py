import os
import json

WARNING_THRESHOLD = float(os.environ.get("WARNING_THRESHOLD", 0.03))
CRITICAL_THRESHOLD = float(os.environ.get("CRITICAL_THRESHOLD", 0.08))


def classify_severity(pass_rate_delta: float) -> str:
    drop = -pass_rate_delta  # a positive 'drop' means things got worse

    if drop >= CRITICAL_THRESHOLD:
        return "critical"
    if drop >= WARNING_THRESHOLD:
        return "warning"
    return "pass"


def update_history_and_check_drift(
    current_pass_rate: float,
    history_path: str = "results/history.json",
    window: int = 7,
    floor: float = 0.90,
) -> dict:
    try:
        with open(history_path) as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(current_pass_rate)
    history = history[-window:]

    with open(history_path, "w") as f:
        json.dump(history, f)

    moving_avg = sum(history) / len(history)
    return {"moving_avg": moving_avg, "slow_drift_warning": moving_avg < floor}