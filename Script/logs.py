
from datetime import datetime, timedelta
import math
import random
import uuid
from constants import log_levels, user_event_types,clients,normal_realms,protocols,resource_types,user_pool, connections, keycloak_scopes, grant_types
from functions import timestamp, timestamp_anomaly,add_contextual_event_details,assign_realm_and_validate_session
from anomalies import generate_brute_force_session,generate_frequent_get_queries_session, generate_sabotage_session, generate_privilege_exploitation_session


def generate_log():
    userId = random.choice(user_pool)
    session_id = str(uuid.uuid4())
    realm = random.choice(normal_realms)
    ip = f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    client_id = random.choice(clients)
    protocol = random.choice(protocols)
    connection = random.choice(connections)
    scope = random.choice(keycloak_scopes)
    grant_type = random.choice(grant_types)

    return {
        "userId": userId,
        "session_id": session_id,
        "realmId": realm,
        "ip": ip,
        "clientId": client_id,
        "protocol": protocol,
        "connection": connection,
        "scope": scope,
        "grant_type": grant_type,
    }


def generate_noise_session(user_id, include_labels):
    logs = []
    context = generate_log()
    noise_event_types = ["LOGIN_ERROR", "FORGOT_PASSWORD", "UPDATE_PROFILE", "RESET_PASSWORD", "CODE_TO_TOKEN_ERROR", "LOGIN"]
    for _ in range(5):
        log = {
            "timestamp": ((random.choice([timestamp_anomaly, timestamp])) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(log_levels),
            "category": "org.keycloak.events",
            "type": random.choice(noise_event_types),
            "realmId": context["realmId"],
            "clientId": context["clientId"],
            "userId": user_id,
            "sessionId": context["session_id"],
        }

        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(
            log, clients, user_id, context)


        if include_labels:
            log["label"] = 0
        logs.append(log)

    return logs

def generate_admin_event_log(include_labels):
    logs = []

    operation = random.choice(["CREATE", "UPDATE", "DELETE", "ACTION"])
    context = generate_log()
    resource_type = random.choice(resource_types)

    # Zuerst immer ein LOGIN-Log
    login_log = {
        "timestamp": ((timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "log_level": "info",
        "category": "org.keycloak.events",
        "type": "LOGIN",
        "realmId": context["realmId"],
        "clientId": context["clientId"],
        "userId": context["userId"],
        "sessionId": context["session_id"],
    }
    login_log = assign_realm_and_validate_session(login_log, "admin")
    login_log = add_contextual_event_details(login_log, clients, "admin", context)

    if include_labels:
        login_log["label"] = 0

    logs.append(login_log)

    for _ in range(4):
        if random.random() < 0.5:
            # Fall A: Admin-Operation mit operationType
            admin_log = {
                "timestamp": ((timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
                "log_level": random.choice(log_levels),
                "category": "org.keycloak.events",
                "authDetails": {
                    "userId": "admin",
                    "ipAddress": context["ip"],
                    "realmId": context["realmId"],
                    "clientId": "security-admin-console",
                    "sessionId": context["session_id"],
                },
                "operationType": operation,
                "resourceType": resource_type,
                "resourcePath": f"{resource_type.lower()}s/{str(uuid.uuid4())}",
            }

            if include_labels:
                admin_log["label"] = 0

            logs.append(admin_log)

        else:
            # Fall B: "Normales" Admin-User-Event wie LOGOUT, TOKEN_REFRESH etc.
            log = {
                "timestamp": ((timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
                "log_level": random.choice(log_levels),
                "category": "org.keycloak.events",
                "type": random.choice(["LOGOUT", "REFRESH_TOKEN", "CODE_TO_TOKEN", "TOKEN_EXCHANGE"]),
                "realmId": context["realmId"],
                "clientId": context["clientId"],
                "userId": context["userId"],
                "sessionId": context["session_id"],
            }
            log = assign_realm_and_validate_session(log, "admin")
            log = add_contextual_event_details(log, clients, "admin", context)
            if include_labels:
                log["label"] = 0

            logs.append(log)

    return logs



def generate_user_session_logs(user_id, include_labels):
    logs = []
    context = generate_log()
    login_log = {
        "timestamp": ((timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "log_level": "info",
        "category": "org.keycloak.events",
        "type": "LOGIN",
        "realmId": context["realmId"],
        "clientId": context["clientId"],
        "userId": context["userId"],
        "sessionId": context["session_id"],
    }
    login_log = assign_realm_and_validate_session(login_log, user_id)
    login_log = add_contextual_event_details(login_log, clients, user_id, context)


    if include_labels:
        login_log["label"] = 0

    logs.append(login_log)

    for _ in range(4):
        event_type = random.choice([et for et in user_event_types if et != "LOGIN"])
        log = {
            "timestamp": ((timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(log_levels),
            "category": "org.keycloak.events",
            "type": event_type,
            "realmId": context["realmId"],
            "clientId": context["clientId"],
            "userId": context["userId"],
            "sessionId": context["session_id"],
        }

        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(
            log, clients, user_id, context)
        
        if include_labels:
            log["label"] = 0
        logs.append(log)

    return logs


def add_random_time_noise(logs, max_noise_seconds=30):
    for log in logs:
        ts_str = log['timestamp']

        # Parse ISO 8601 Format (mit T und Zeitzone)
        ts = datetime.fromisoformat(ts_str)

        noise = random.uniform(-max_noise_seconds, max_noise_seconds)
        ts_noisy = ts + timedelta(seconds=noise)

        # Zurück speichern als ISO Format (oder ohne Zeitzone, je nach Bedarf)
        log['timestamp'] = ts_noisy.isoformat()


def generate_logs_with_sessions(num_sessions, anomaly_probability, include_labels):
    logs = []

    # Anzahl Anomalie-Sessions (mindestens 1, wenn anomaly_probability > 0)
    num_anomaly = math.ceil(num_sessions * anomaly_probability / 100) if anomaly_probability > 0 else 0

    # Fixe Werte für Noise (30%) und Admin (10%)
    #num_noise = int(num_sessions * 0.3)
    num_admin = int(num_sessions * 0.1)

    # User Sessions bekommen den Rest
    num_user = num_sessions - (num_anomaly + num_admin)

    # Falls num_user negativ (Überbelegung), dann Fehler ausgeben
    if num_user < 0:
        raise ValueError("Summe der Anteile überschreitet 100%! anomaly_probability zu hoch.")

    # Noise Sessions
    # for _ in range(num_noise):
    #     user_id = random.choice(user_pool)
    #     logs.extend(generate_noise_session(user_id, include_labels))

    # Admin Sessions
    for _ in range(num_admin):
        logs.extend(generate_admin_event_log(
            include_labels=include_labels
        ))

    # User Sessions (normal)
    for _ in range(num_user):
        user_id = random.choice(user_pool)
        logs.extend(generate_user_session_logs(user_id, include_labels))

    # Anomalie Sessions
    anomaly_types = ['privilege_exploitation', 'brute_force', 'sabotage', 'same_resource']
    for _ in range(num_anomaly):
        user_id = random.choice(user_pool)
        attack_type = random.choice(anomaly_types)

        if attack_type == 'privilege_exploitation':
            logs.extend(generate_privilege_exploitation_session(user_id, include_labels))
        elif attack_type == 'brute_force':
            logs.extend(generate_brute_force_session(include_labels))
        elif attack_type == 'sabotage':
            logs.extend(generate_sabotage_session(user_id, include_labels))
        elif attack_type == 'same_resource':
            logs.extend(generate_frequent_get_queries_session(user_id, include_labels))

    add_random_time_noise(logs, max_noise_seconds=30)
    # Nach Zeit sortieren
    logs.sort(key=lambda x: x['timestamp'])
    return logs
