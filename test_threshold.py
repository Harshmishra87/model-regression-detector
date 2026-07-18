from src.thresholds import classify_severity, update_history_and_check_drift

# Your actual diff result from Step 14
severity = classify_severity(pass_rate_delta=0.01)
print("Severity:", severity)

drift_check = update_history_and_check_drift(current_pass_rate=0.93)
print("Drift check:", drift_check)