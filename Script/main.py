import json
from logs import generate_logs_with_sessions

train_logs = generate_logs_with_sessions(num_sessions=750, anomaly_probability=0.0, include_labels=False)
val_logs   = generate_logs_with_sessions(num_sessions=125, anomaly_probability=0.0, include_labels=True)
test_logs  = generate_logs_with_sessions(num_sessions=125, anomaly_probability=0.0008, include_labels=True)
#train_logs_for_isolated_models = generate_logs_with_sessions(num_sessions=750, anomaly_probability=0.05, include_labels=False)

# Logs speichern
with open("script_train_logs.json", "w") as f:
    json.dump(train_logs, f, indent=2)

with open("script_val_logs.json", "w") as f:
    json.dump(val_logs, f, indent=2)

with open("script_test_logs.json", "w") as f:
    json.dump(test_logs, f, indent=2)

# with open("train_logs_isolated.json", "w") as f:
#     json.dump(train_logs_for_isolated_models, f, indent=2)

# Logs laden
with open("script_train_logs.json") as f:
    logs_train = json.load(f)

with open("script_val_logs.json") as f:
    logs_val = json.load(f)

with open("script_test_logs.json") as f:
    logs_test = json.load(f)

# with open("train_logs_isolated.json") as f:
#     logs_train_isolated = json.load(f)
