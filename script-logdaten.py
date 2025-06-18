import random
from datetime import datetime, timedelta
import pytz
import json

def generate_log_entry(log_type, is_anomaly=False, include_label=False):
    tz = pytz.timezone('Europe/Berlin')

    roles_normal = ['user', 'viewer', 'member', 'offline_access', 'uma_authorization']
    roles_anomaly = ['admin', 'realm-admin', 'manage-users', 'manage-realm', 'manage-clients']

    normal_auth_methods = ['openid-connect', 'password', 'saml']
    anomaly_auth_methods = ['identity-provider-login', 'unknown', '']

    normal_connections = ['default', 'ldap', 'saml']
    anomaly_connections = ['unknown', 'fake-ldap', 'invalid-provider']

    normal_realms = ['master', 'app-users', 'frontend', 'internal']
    anomaly_realms = ['deleted-realm', 'external-hack-realm', 'unknown']

    normal_hours = list(range(8, 19))
    anomaly_hours = list(range(0, 6))

    hour = random.choice(anomaly_hours if is_anomaly else normal_hours)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    timestamp = datetime.now(tz).replace(hour=hour, minute=minute, second=second, microsecond=0) - timedelta(days=random.randint(0, 5))

    roles = random.sample(roles_anomaly + roles_normal if is_anomaly else roles_normal, k=random.randint(1, 3))
    if is_anomaly and 'admin' not in roles and random.random() < 0.5:
        roles.append('admin')

    log = {
        "timestamp": timestamp.isoformat(),
        "log_type": log_type,
        "userId": f"user_{random.randint(1, 50)}",
        "ipAddress": (
            f"{random.randint(200, 255)}.{random.randint(100,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
            if is_anomaly else
            f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        ),
        "roles": roles,
        "realmId": random.choice(anomaly_realms if is_anomaly else normal_realms),
        "clientId": "frontend-app",
        "authMethod": random.choice(anomaly_auth_methods if is_anomaly else normal_auth_methods),
        "authType": "code",
        "details": {},
        "user_agent": "Mozilla/5.0 (compatible)"
    }

    if log_type == "user_event":
        if is_anomaly:
            types = [
                "LOGIN", "LOGOUT", "REGISTER", "REGISTER_ERROR", "CODE_TO_TOKEN",
                "TOKEN_REFRESH", "UPDATE_PROFILE", "UPDATE_PASSWORD",
                "SEND_VERIFY_EMAIL", "SEND_RESET_PASSWORD",
                "CUSTOM_REQUIRED_ACTION", "EXECUTE_ACTIONS",
                "IDENTITY_PROVIDER_LOGIN", "IDP_LINK_ACCOUNT",
                "RESTART_AUTHENTICATION", "LOGIN_ERROR"
            ]
            weights = [
                10, 10, 5, 3, 10,
                10, 5, 5,
                1, 1,
                1, 1,
                1, 1,
                1, 5
            ]
            event_type = random.choices(types, weights=weights, k=1)[0]
        else:
            types = ["LOGIN", "LOGOUT", "TOKEN_REFRESH", "CODE_TO_TOKEN"]
            weights = [10, 10, 10, 10]
            event_type = random.choices(types, weights=weights, k=1)[0]

        log.update({
            "type": event_type,
            "details": {
                "connection": random.choice(anomaly_connections if is_anomaly else normal_connections),
                "user_agent": log["user_agent"]
            }
        })

    elif log_type == "admin_event":
        operations = ["CREATE", "UPDATE", "DELETE", "ACTION"]
        op_weights = [3, 3, 1, 3]
        operation = random.choices(operations, weights=op_weights, k=1)[0]

        log.update({
            "operation": operation,
            "adminId": f"admin_{random.randint(1, 5)}",
            "resource": random.choice(["users", "clients", "roles", "groups", "authentication", "realms"]),
            "resource_path": f"{random.choice(['users', 'clients', 'roles'])}/{random.randint(1000,9999)}",
            "details": {
                "realm": log["realmId"],
                "connection": random.choice(anomaly_connections if is_anomaly else normal_connections),
                "user_agent": log["user_agent"]
            }
        })

    if include_label:
        log["label"] = 1 if is_anomaly else 0

    return log

def generate_user_session(is_anomaly=False, user_id=None, include_label=False):
    tz = pytz.timezone('Europe/Berlin')
    session_logs = []
    session_length = random.randint(5, 10)
    user_id = user_id or f"user_{random.randint(1, 50)}"
    base_time = datetime.now(tz) - timedelta(days=random.randint(0, 5))

    roles_before = ['user', 'viewer', 'member']
    roles_after = ['admin', 'realm-admin', 'manage-clients']

    if is_anomaly:
        # Beginne mit 5 Login-Fehlern
        for _ in range(5):
            log = generate_log_entry("user_event", is_anomaly=True, include_label=include_label)
            log["type"] = "LOGIN_ERROR"
            log["timestamp"] = (base_time + timedelta(minutes=_)).isoformat()
            log["userId"] = user_id
            session_logs.append(log)

        # Danach 3 Zugriffsversuche
        for _ in range(3):
            log = generate_log_entry("user_event", is_anomaly=True, include_label=include_label)
            log["type"] = "IDP_LINK_ACCOUNT"
            log["timestamp"] = (base_time + timedelta(minutes=5 + _)).isoformat()
            log["userId"] = user_id
            session_logs.append(log)

        # Plötzlicher Rollenwechsel & Zugriff auf sensible Daten
        admin_log = generate_log_entry("admin_event", is_anomaly=True, include_label=include_label)
        admin_log["roles"] = roles_after
        admin_log["timestamp"] = (base_time + timedelta(minutes=9)).isoformat()
        admin_log["userId"] = user_id
        admin_log["ipAddress"] = "255.255.255.255"  # unsichtbar/fake
        admin_log["operation"] = "DELETE"
        admin_log["resource"] = "realms"
        session_logs.append(admin_log)
    else:
        # Normale Session
        for i in range(session_length):
            log = generate_log_entry("user_event", is_anomaly=False, include_label=include_label)
            log["timestamp"] = (base_time + timedelta(minutes=i)).isoformat()
            log["userId"] = user_id
            session_logs.append(log)

    return session_logs


def generate_logs_with_sessions(num_sessions=10000, anomaly_ratio=0.1, include_labels=False):
    logs = []
    num_anomalies = int(num_sessions * anomaly_ratio)
    num_normals = num_sessions - num_anomalies

    for _ in range(num_normals):
        logs.extend(generate_user_session(is_anomaly=False, include_label=include_labels))
    for _ in range(num_anomalies):
        logs.extend(generate_user_session(is_anomaly=True, include_label=include_labels))

    logs.sort(key=lambda x: x['timestamp'])  # sortiere für zeitlichen Kontext
    return logs


train_logs = generate_logs_with_sessions(num_sessions=7000, anomaly_ratio=0.0, include_labels=True)
val_logs   = generate_logs_with_sessions(num_sessions=1500, anomaly_ratio=0.01, include_labels=True)
test_logs  = generate_logs_with_sessions(num_sessions=1500, anomaly_ratio=0.2, include_labels=True)

# Speichern
with open("train_logs.json", "w") as f:
    json.dump(train_logs, f, indent=2)

with open("val_logs.json", "w") as f:
    json.dump(val_logs, f, indent=2)

with open("test_logs.json", "w") as f:
    json.dump(test_logs, f, indent=2)
