
from datetime import timedelta
import random
from constants import admin_operations,client_roles,client_scopes,clients,connections,log_levels,names,normal_realms,protocols,realm_roles,resource_types,user_event_types,user_pool
from functions import label_if_multiple_admins,timestamp, timestamp_anomaly,add_admin_roles_and_metadata,add_contextual_event_details,allowed_client_event_map,anomaly_hour,assign_realm_and_validate_session,clean_irrelevant_fields


def generate_noise_session(user_id, include_labels):
    logs = []
    sequence = [
        random.choice(["LOGIN_ERROR", "FORGOT_PASSWORD", "UPDATE_PROFILE", "RESET_PASSWORD", "CODE_TO_TOKEN_ERROR"])
        for _ in range(10)
    ]

    for event_type in sequence:
        log = {
            "timestamp": (timestamp_anomaly + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(log_levels),
            "category": "org.keycloak.events",
            "type": event_type,
            "realmId": random.choice(normal_realms),
            "realmName": random.choice(normal_realms),
            "clientId": random.choice(clients),
            "userId": user_id,
            "sessionId": f"session_{random.randint(1000,9999)}",
            "ipAddress": f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "authMethod": random.choice(protocols),

        }
        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)
        if include_labels:
            log["label"] = 0
        if label_if_multiple_admins(logs):
            log["label"] = 1
        logs.append(log)

    return logs

def generate_normal_user_log(user_id, include_labels):
    logs = []

    # Haupt-Log (Login etc.)
    for _ in range(10):
        log = {
            "timestamp": (timestamp + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(log_levels),
            "category": "org.keycloak.events",
            "type": "LOGIN",
            "realmId": random.choice(normal_realms),
            "realmName": random.choice(normal_realms),
            "clientId": random.choice(clients),
            "userId": user_id,
            "sessionId": f"session_{random.randint(1000,9999)}",
            "ipAddress": f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "authMethod": 'openid-connect' or 'saml',
        }
        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)

        if include_labels:
            log["label"] = 0
        if label_if_multiple_admins(logs):
            log["label"] = 1
        logs.append(log)

        # Noise hinzufügen (10–30% Wahrscheinlichkeit)
        if random.random() < 0.2:
            logs.extend(generate_noise_session(user_id, include_labels))

    return logs


def get_unusual_ip():
    first_octet = random.choice([198, 203])
    second_octet = random.randint(0, 255)
    third_octet = random.randint(0, 255)
    fourth_octet = random.randint(1, 254)
    return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"


def generate_brute_force_session(include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    client = 'login-app'

    for _ in range(random.randint(5, 15)):
        log = {
            "timestamp":((timestamp_anomaly or timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "warn",
            "category": "org.keycloak.events",
            "type": "LOGIN_ERROR",
            "realmId": realm,
            "realmName": realm_name,
            "clientId": client,
            "sessionId": f"session_{random.randint(1000,9999)}",
            "ipAddress": f"{get_unusual_ip() or random.randint(1000,9999)}",
            "error": "invalid_credentials",
            "authMethod": random.choice(protocols),
        }
        if include_labels:
            log["label"] = 1
        logs.append(log)
    return logs


def generate_privilege_exploitation_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    admin_client = 'admin-cli'
    escalated_roles = ['admin', 'realm-admin', 'manage-users']
    session_id = f"session_{random.randint(1000, 9999)}"
    anomaly_event_types = [
        "LOGIN", "IMPERSONATE", "IMPERSONATE_ERROR"
    ]
    
    number_of_events = random.randint(5, 15)

    for _ in range(number_of_events):
        event = random.choice(anomaly_event_types)
        log = {
            "timestamp":((timestamp_anomaly or timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "info" or "error",
            "category": "org.keycloak.events",
            "type": event,
            "realmId": realm,
            "realmName": realm_name,
            "clientId": admin_client,
            "userId": user_id,
            "sessionId": session_id,
            "ipAddress": f"{get_unusual_ip() or random.randint(1000,9999)}",
            "roles": escalated_roles,
            "authMethod": random.choice(protocols),
            "resourceType": random.choice(resource_types),
            "operationType": random.choice(admin_operations),
        }
        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)

        if include_labels:
            log["label"] = 1
        logs.append(log)
    log = add_admin_roles_and_metadata(log)
    return logs


def generate_sabotage_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    admin_client = 'admin-cli'
    sabotage_events = [
        "UPDATE_PASSWORD",
        "RESET_PASSWORD",
        "FORGOT_PASSWORD",
        "UPDATE_PROFILE",
        "UPDATE_EMAIL",
        "VERIFY_EMAIL",
        "BRUTE_FORCE_ERROR",
        "BRUTE_FORCE_RESET",
    ]
    session_id = f"session_{random.randint(1000, 9999)}"
    number_of_events = number_of_events = random.randint(5, 15)

    for _ in range(number_of_events):
        event_type = random.choice(sabotage_events)
        log = {
            "timestamp":((timestamp_anomaly or timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "info" or "error",
            "category": "org.keycloak.events",
            "type": event_type,
            "realmId": realm,
            "realmName": realm_name,
            "clientId": admin_client,
            "userId": user_id,
            "sessionId": session_id,
            "ipAddress": f"{get_unusual_ip() or random.randint(1000,9999)}",
            "authMethod": random.choice(protocols),
            "resourceType": random.choice(resource_types),
            "operationType": random.choice(admin_operations),
        }
        log = assign_realm_and_validate_session(log, user_id)
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)

        if include_labels:
            log["label"] = 1
        logs.append(log)
    log = add_admin_roles_and_metadata(log)

    return logs

def generate_frequent_get_queries_session(user_id, include_labels):
    logs = []
    realm = random.choice(normal_realms)
    realm_name = realm
    client_id = random.choice(clients)  # feste Quelle für häufige Abfragen
    session_id = f"session_{random.randint(1000, 9999)}"
    frequent_resource = random.choice(resource_types)  # z.B. "users", "clients"

    number_of_events = random.randint(5, 15)

    for _ in range(number_of_events):
        # 80 % derselbe resourceType & clientId
        if random.random() < 0.8:
            resource_type = frequent_resource
            client = client_id
        else:
            resource_type = random.choice(resource_types)
            client = random.choice(clients)

        log = {
            "timestamp":((timestamp_anomaly or timestamp) + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": random.choice(log_levels),
            "category": "org.keycloak.events",
            "realmId": realm,
            "realmName": realm_name,
            "clientId": client,
            "userId": user_id,
            "sessionId": session_id,
            "ipAddress": f"{get_unusual_ip() or random.randint(1000,9999)}",
            "authMethod": random.choice(protocols),
            "resourceType": resource_type,
            "operationType": "GET",
        }

        if include_labels:
            log["label"] = 1

        logs.append(log)

    return logs


def generate_logs_with_sessions(num_sessions, anomaly_probability, include_labels):
    logs = []

    for _ in range(num_sessions):
        if random.random() < anomaly_probability:
            attack_type = random.choice(['privilege_exploitation', 'brute_force', 'sabotage', 'same_resource'])
            user_id = random.choice(user_pool)

            if attack_type == 'privilege_exploitation':
                logs.extend(generate_privilege_exploitation_session(
                    user_id=user_id,
                    include_labels=include_labels
                ))

            elif attack_type == 'brute_force':
                logs.extend(generate_brute_force_session(
                    include_labels=include_labels
                ))
            elif attack_type == 'sabotage':
                logs.extend(generate_sabotage_session(
                    user_id=user_id,
                    include_labels=include_labels
                ))
            elif attack_type == 'same_resource':
                logs.extend(generate_frequent_get_queries_session(
                    user_id=user_id,
                    include_labels=include_labels
                ))
        else:
            user_id = random.choice(user_pool)
            logs.extend(generate_normal_user_log(
                user_id=user_id,
                include_labels=include_labels
            ))

    #random.shuffle(logs)
    logs.sort(key=lambda x: x['timestamp'])
    return logs
