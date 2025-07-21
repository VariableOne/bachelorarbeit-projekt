from datetime import datetime, timedelta
import random
import uuid
from functions import timestamp_anomaly, timestamp
from constants import normal_realms, clients, protocols, user_pool, resource_types, connections, grant_types,keycloak_scopes

def get_unusual_ip():
    first_octet = random.choice([198, 203])
    second_octet = random.randint(0, 255)
    third_octet = random.randint(0, 255)
    fourth_octet = random.randint(1, 254)
    return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"

def generate_brute_force_session(include_labels):
    logs = []

    for _ in range(5):
        realm = random.choice(normal_realms)
        username = random.choice(user_pool)
        log = {
            "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "error",
            "category": "org.keycloak.events",
            "type": "LOGIN_ERROR",
            "realmId": realm,
            "realmName": realm,  # falls realmName gleich realmId ist
            "clientId": random.choice(clients),
            "ipAddress": get_unusual_ip(),
            "error": "invalid_credentials",
            "username": username,
            "details": {
                "auth_type": random.choice(protocols),  # richtig so
                "connection": random.choice(connections),
                "scope": random.choice(keycloak_scopes),
                "grant_type": random.choice(grant_types),
                "refresh_token_id": str(uuid.uuid4()),
                "code_id": str(uuid.uuid4())
            }
        }

        if include_labels:
            log["label"] = 1
        logs.append(log)
    return logs


def generate_privilege_exploitation_session(user_id, include_labels):
    logs = []
    realm = random.choice(normal_realms)
    session_id = str(uuid.uuid4())
    ip = f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

    # ➤ Start mit einem normalen LOGIN des Users
    login_log = {
        "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "category": "org.keycloak.events",
        "log_level": random.choice(["info", "error"]),
        "type": "LOGIN",
        "realmId": realm,
        "clientId": random.choice(clients),
        "userId": user_id,
        "sessionId": session_id,
        "ipAddress": ip,
    }
    if include_labels:
        login_log["label"] = 1
    logs.append(login_log)

    # ➤ Danach folgen Admin-artige Events mit Anomalien
    anomaly_event_types = ["IMPERSONATE", "IMPERSONATE_ERROR"]

    for _ in range(4):
        log = {
        "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "log_level": random.choice(["info", "error"]),
        "category": "org.keycloak.events",
        "type": random.choice(anomaly_event_types),
        "realmId": realm,
        "clientId": random.choice(clients),
        "userId": user_id,
        "sessionId": session_id,
        "ipAddress": ip,
    }

        if include_labels:
            log["label"] = 1

        logs.append(log)

    return logs



def generate_sabotage_session(user_id, include_labels):
    logs = []
    session_id = str(uuid.uuid4())
    realm = 'master'
    ip = f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

    sabotage_events = [
    "RESET_PASSWORD",
    "UPDATE_PROFILE",
    "UPDATE_PASSWORD",
    "VERIFY_EMAIL",
    "REMOVE_CREDENTIAL"
    ]


    login_log = {
        "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "category": "org.keycloak.events",
        "category": "org.keycloak.events",
        "type": "LOGIN",
        "realmId": realm,
        "clientId": random.choice(clients),
        "userId": user_id,
        "sessionId": session_id,
        "ipAddress": ip,
    }
    if include_labels:
        login_log["label"] = 1
    logs.append(login_log)

    for _ in range(4):
        event_type = random.choice(sabotage_events)

        log = {
        "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "log_level": random.choice(["info", "error"]),
        "category": "org.keycloak.events",
        "type": event_type,
        "realmId": realm,
        "clientId": random.choice(clients),
        "userId": user_id,
        "sessionId": session_id,
        "ipAddress": ip,
    }
        if include_labels:
            log["label"] = 1

        logs.append(log)

    return logs


def generate_frequent_get_queries_session(user_id, include_labels):
    logs = []
    realm = random.choice(normal_realms)
    session_id = str(uuid.uuid4())
    admin_client = 'security-admin-console'  # Admin Client festlegen
    frequent_resource = random.choice(resource_types)  # z.B. "users", "clients"
    ip = f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    operation = "ACTION"

    login_log = {
        "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
        "type": "LOGIN",
        "category": "org.keycloak.events",
        "realmId": realm,
        "clientId": random.choice(clients),
        "userId": "admin",
        "sessionId": session_id,
        "ipAddress": ip,
    }
    if include_labels:
        login_log["label"] = 1
    logs.append(login_log)

    for _ in range(4):
        log = {
            "timestamp": (random.choice([timestamp, timestamp_anomaly]) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(["info", "error"]),
            "category": "org.keycloak.events",
            "realmId": realm,
            "authDetails": {
                "userId": "admin",
                "ipAddress": random.choice([get_unusual_ip(), ip]),
                "realmId": realm,
                "clientId": admin_client,
                "sessionId": session_id
            },
            "operationType": operation,
            "resourceType": frequent_resource,
            "resourcePath": f"{frequent_resource.lower()}s/{str(uuid.uuid4())}",
        }

        if include_labels:
            log["label"] = 1

        logs.append(log)

    return logs