import random
from datetime import datetime, timedelta
import pytz
import json
from datetime import datetime, time, timedelta


normal_realms = [    
    'bosch',
    'telekom'
    ]

    # Standard Clients in Keycloak
clients = [
        'account',               # Benutzer Account Management UI
        'admin-cli',             # CLI für Admins
        'broker',                # Identity Broker Client
        'realm-management',      # Realm Management Console Client
        'security-admin-console' # Keycloak Admin UI
    ]

    # Realm Roles (Beispiele aus Keycloak realm-level roles)
realm_roles = [
        'admin',
        'realm-admin',
        'create-realm',
        'impersonation',
        'manage-users',
        'manage-realm',
        'manage-clients',
        'view-users',
        'manage-events',
        'query-users',
        'manage-authorization',
        'admin-cli',
        'offline_access',
        'uma_authorization',
    ]

    # Client Roles (Beispiele aus Keycloak client-level roles)
client_roles = [
        'manage-account',
        'view-profile',
        'manage-account-links',
        'view-consent',
        'manage-consent',
        'view-realm',
        'manage-realm',
        'view-users',
        'manage-users',
        'manage-clients',
        'view-clients',
        'manage-events',
        'manage-authorization',
        'create-client',
        'manage-account:manage-account',
        'account:view-profile',
    ]

    # Client Scopes (Keycloak Standard Scopes)
client_scopes = [
        'profile',
        'email',
        'roles',
        'web-origins',
        'offline_access',
        'microprofile-jwt',  # wenn aktiviert
    ]


    # Auth Protocols (Keycloak unterstützt vor allem)
protocols = [
        'openid-connect',
        'saml',
        'oauth2-client-credentials',
        'password',
        'otp',
        'browser',
        'code',
    ]

    # Connections (User Federation Providers & Identity Providers)
connections = [
        'default',
        'ldap',
        'kerberos',
        'saml',
        'github',
        'google',
        'facebook',
        'twitter',
        'openid-connect',
    ]

user_event_types = [
    "LOGIN",
    "LOGIN_ERROR",
    "LOGOUT",
    "REGISTER",
    "REGISTER_ERROR",
    "UPDATE_PASSWORD",
    "UPDATE_PROFILE",
    "UPDATE_EMAIL",
    "VERIFY_EMAIL",
    "FORGOT_PASSWORD",
    "RESET_PASSWORD",
    "CODE_TO_TOKEN",
    "CODE_TO_TOKEN_ERROR",
    "CLIENT_LOGIN",
    "CLIENT_LOGIN_ERROR",
    "REVOKE_GRANT",
    "IMPERSONATE",
    "IMPERSONATE_ERROR",
    "BRUTE_FORCE_ERROR",
    "BRUTE_FORCE_RESET",
    "TOKEN_REFRESH"
]

log_levels = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "fatal"
]


admin_operations = ["CREATE", "UPDATE", "DELETE", "ACTION"]
resource_types = ["users", "clients", "roles", "groups", "authentication"]

with open("names.json") as f:
    names = json.load(f)
    user_pool = names[:50]

# Beispiel
normal_hours = list(range(8, 19))
anomaly_hours = list(range(0, 6))

base_time = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=random.randint(0,5))
base_time = base_time.replace(hour=random.choice(anomaly_hours), minute=random.randint(0,59), second=random.randint(0,59), microsecond=0)

def random_time_from_hours(hours):
    tz = pytz.timezone('Europe/Berlin')
    today = datetime.now(tz)
    hour = random.choice(hours)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    dt = today.replace(hour=hour, minute=minute, second=second, microsecond=0)
    dt -= timedelta(days=random.randint(0, 5))
    return dt.isoformat()

def enrich_log_with_event_details(log):
    event_type = log.get("type", "")

    details = {}
    error = None

    if event_type in ["LOGIN", "LOGIN_ERROR", "REGISTER", "REGISTER_ERROR"]:
        details["auth_method"] = random.choice(["openid-connect", "saml"])
        details["auth_type"] = random.choice(["code", "implicit"])
        if "ERROR" in event_type:
            error = random.choice(["invalid_credentials", "user_not_found"])

    elif event_type == "VERIFY_EMAIL":
        details["email"] = f"user{random.randint(1,100)}@example.com"

    elif event_type in ["FORGOT_PASSWORD", "RESET_PASSWORD"]:
        details["email"] = f"user{random.randint(1,100)}@example.com"

    elif event_type in ["IMPERSONATE", "IMPERSONATE_ERROR"]:
        details["impersonator"] = f"admin_{random.randint(1,10)}"
        if "ERROR" in event_type:
            error = random.choice(["impersonation_denied"])

    elif event_type == "CODE_TO_TOKEN":
        details["client_auth_method"] = random.choice(["client_secret_basic", "client_secret_post"])

    elif event_type == "CODE_TO_TOKEN_ERROR":
        details["client_auth_method"] = random.choice(["client_secret_basic", "client_secret_post"])
        error = random.choice(["invalid_grant", "unauthorized_client"])

    elif event_type in ["CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH"]:
        details["client_id"] = random.choice(clients)
        if "ERROR" in event_type:
            error = random.choice(["invalid_client", "unauthorized_client"])

    elif event_type == "BRUTE_FORCE_ERROR":
        details["username"] = f"user{random.randint(1,50)}"
        error = "brute_force_detected"

    elif event_type == "BRUTE_FORCE_RESET":
        details["username"] = f"user{random.randint(1,50)}"

    elif event_type == "REVOKE_GRANT":
        details["client_id"] = random.choice(clients)

    # Update log dictionary
    log["details"] = details
    if error:
        log["error"] = error

    # Optional: roles entfernen, wenn nicht gewünscht
    if event_type == "LOGIN" and "roles" in log:
        del log["roles"]

    return log


def generate_normal_user_log(user_id, include_labels):

    roles_sample = random.sample(client_roles, k=random.randint(1, 3))
    log = {
        "timestamp": random_time_from_hours(normal_hours),
        "log_level": random.choice(log_levels),
        "category": "org.keycloak.events",
        "type": random.choice(user_event_types),
        "realmId": random.choice(normal_realms),
        "realmName": random.choice(normal_realms),
        "clientId": random.choice(clients),
        "userId": user_id or f"user_{random.randint(1, 50)}",
        "sessionId": f"session_{random.randint(1000,9999)}",  # optional, wie in Java-Log
        "ipAddress": f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "error": None,
        "roles": roles_sample,
        "authMethod": random.choice(protocols),
        "authType": "code",
        "resourceType": random.choice(resource_types),
        "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
    }

    #log = enrich_log_with_event_details(log)

    if include_labels:
        log["label"] = 0

    return log


def generate_normal_admin_log(admin_id, include_labels):
    roles_sample_admin = random.sample(client_roles + ['admin'], k=random.randint(1, 3))
    log = {
        "timestamp": random_time_from_hours(normal_hours),
        "log_level": random.choice(log_levels),
        "category": "org.keycloak.events",
        "type": random.choice(["admin_event", "admin_event_error"] + user_event_types),
        "operationType": random.choice(admin_operations),
        "realmId": random.choice(["master"] + normal_realms),
        "realmName": random.choice(["master"] + normal_realms),
        "clientId": random.choice(clients),
        "userId": admin_id,
        "ipAddress": f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "resourceType": random.choice(resource_types),
        "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
        "error": None,
        "roles": roles_sample_admin,
        "authMethod": "openid-connect",
        "authType": "code"
    }

    #log = enrich_log_with_event_details(log)

    if include_labels:
        log["label"] = 0 

    return log


def generate_privilege_escalation_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    admin_client = 'admin-cli'
    escalated_roles = ['admin', 'realm-admin']

    base_time = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=random.randint(0, 5))
    base_time = base_time.replace(hour=random.choice(anomaly_hours), minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)

    sequence = [
        {"minutes": 0, "type": "LOGIN", "clientId": "account", "roles": escalated_roles},
        {"minutes": 4, "type": "IMPERSONATE", "clientId": admin_client, "roles": escalated_roles},
        {"minutes": 6, "type": "REVOKE_GRANT", "clientId": admin_client, "roles": escalated_roles},
    ]

    for i in range(2):
        for step in sequence:
            timestamp = base_time + timedelta(minutes=step["minutes"] + i * 10)
            log = {
                "timestamp": timestamp.isoformat(),
                "log_level": "info",
                "category": "org.keycloak.events",
                "type": step["type"],
                "realmId": realm,
                "realmName": realm_name,
                "clientId": step["clientId"],
                "userId": user_id,
                "sessionId": f"session_{random.randint(1000,9999)}",
                "ipAddress": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
                "error": None,
                "roles": step["roles"],
                "authMethod": "openid-connect",
                "authType": "code",
                "operationType": None,
                "resourceType": random.choice(resource_types),
                "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
            }
            if include_labels:
                log["label"] = 1
            logs.append(log)
    return logs

def generate_lateral_movement_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    target_client = 'realm-management'
    anomalous_roles = ['impersonation', 'manage-users']

    base_time = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=random.randint(0, 5))
    base_time = base_time.replace(hour=random.choice(anomaly_hours), minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)

    sequence = [
        {"minutes": 0, "type": "LOGIN", "clientId": "account", "roles": anomalous_roles},
        {"minutes": 5, "type": "IMPERSONATE", "clientId": target_client, "roles": anomalous_roles},
        {"minutes": 10, "type": "UPDATE_PROFILE", "clientId": target_client, "roles": anomalous_roles},
    ]

    for i in range(2):
        for step in sequence:
            timestamp = base_time + timedelta(minutes=step["minutes"] + i * 15)
            log = {
                "timestamp": timestamp.isoformat(),
                "log_level": "info",
                "category": "org.keycloak.events",
                "type": step["type"],
                "realmId": realm,
                "realmName": realm_name,
                "clientId": step["clientId"],
                "userId": user_id,
                "sessionId": f"session_{random.randint(1000,9999)}",
                "ipAddress": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
                "error": None,
                "roles": step["roles"],
                "authMethod": "openid-connect",
                "authType": "code",
                "operationType": None,
                "resourceType": random.choice(resource_types),
                "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
            }
            if include_labels:
                log["label"] = 1
            logs.append(log)
    return logs

def generate_credential_access_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    security_client = 'security-admin-console'
    anomaly_roles = ['view-users']

    base_time = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=random.randint(0, 5))
    base_time = base_time.replace(hour=random.choice(anomaly_hours), minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)

    sequence = [
        {"minutes": 0, "type": "LOGIN", "clientId": "account", "roles": anomaly_roles},
        {"minutes": 3, "type": "VIEW_CONSENT", "clientId": security_client, "roles": anomaly_roles},
        {"minutes": 7, "type": "VIEW_PROFILE", "clientId": security_client, "roles": anomaly_roles},
    ]

    for i in range(2):
        for step in sequence:
            timestamp = base_time + timedelta(minutes=step["minutes"] + i * 12)
            log = {
                "timestamp": timestamp.isoformat(),
                "log_level": "info",
                "category": "org.keycloak.events",
                "type": step["type"],
                "realmId": realm,
                "realmName": realm_name,
                "clientId": step["clientId"],
                "userId": user_id,
                "sessionId": f"session_{random.randint(1000,9999)}",
                "ipAddress": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
                "error": None,
                "roles": step["roles"],
                "authMethod": "openid-connect",
                "authType": "code",
                "operationType": None,
                "resourceType": random.choice(resource_types),
                "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
            }
            if include_labels:
                log["label"] = 1
            logs.append(log)
    return logs

def generate_defense_evasion_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    security_client = 'security-admin-console'
    evasion_roles = ['admin', 'manage-events']

    base_time = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=random.randint(0, 5))
    base_time = base_time.replace(hour=random.choice(anomaly_hours), minute=random.randint(0, 59), second=random.randint(0, 59), microsecond=0)

    sequence = [
        {"minutes": 0, "type": "LOGIN", "clientId": "account", "roles": evasion_roles},
        {"minutes": 3, "type": "UPDATE_PROFILE", "clientId": security_client, "roles": evasion_roles},
        {"minutes": 7, "type": "UPDATE_EMAIL", "clientId": security_client, "roles": evasion_roles},
    ]

    for i in range(2):
        for step in sequence:
            timestamp = base_time + timedelta(minutes=step["minutes"] + i * 12)
            log = {
                "timestamp": timestamp.isoformat(),
                "log_level": "info",
                "category": "org.keycloak.events",
                "type": step["type"],
                "realmId": realm,
                "realmName": realm_name,
                "clientId": step["clientId"],
                "userId": user_id,
                "sessionId": f"session_{random.randint(1000,9999)}",
                "ipAddress": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
                "error": None,
                "roles": step["roles"],
                "authMethod": "openid-connect",
                "authType": "code",
                "operationType": None,
                "resourceType": random.choice(resource_types),
                "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
            }
            if include_labels:
                log["label"] = 1
            logs.append(log)
    return logs


def generate_logs_with_sessions(num_sessions, anomaly_ratio, include_labels):
    logs = []
    admin_ratio = 0.09
    num_anomalies = int(num_sessions * anomaly_ratio)
    num_admins = int(num_sessions * admin_ratio)
    num_normals = num_sessions - num_anomalies - num_admins
    # Normale User Logs (einfache normale User Logs, keine Sessions)
    for _ in range(num_normals):
        user_id = random.choice(user_pool)
        logs.append(generate_normal_user_log(user_id=user_id, include_labels=include_labels))

    # Anomale User Sessions (z.B. Privilege Escalation, Lateral Movement ...)
    for _ in range(num_anomalies):
        attack_type = random.choice(['privilege_escalation', 'lateral_movement', 'credential_access', 'defense_evasion'])
        user_id = random.choice(user_pool)

        if attack_type == 'privilege_escalation':
            logs.extend(generate_privilege_escalation_session(
                user_id=user_id,
                include_labels=include_labels
            ))
        elif attack_type == 'credential_access':
            logs.extend(generate_credential_access_session(
                user_id=user_id,
                include_labels=include_labels
            ))
        elif attack_type == 'defense_evasion':
            logs.extend(generate_defense_evasion_session(
                user_id=user_id,
                include_labels=include_labels
            ))
        else:
            logs.extend(generate_lateral_movement_session(
                user_id=user_id,
                include_labels=include_labels
            ))

    # Admin Logs (nur einzelne Admin Events)
    for _ in range(num_admins):
        admin_id = "admin"
        logs.append(generate_normal_admin_log(admin_id=admin_id, include_labels=include_labels))

    logs.sort(key=lambda x: x['timestamp'])
    random.shuffle(logs)
    return logs


train_logs = generate_logs_with_sessions(num_sessions=40000, anomaly_ratio=0.0, include_labels=False)
val_logs   = generate_logs_with_sessions(num_sessions=5000, anomaly_ratio=0.05, include_labels=True)
test_logs  = generate_logs_with_sessions(num_sessions=5000, anomaly_ratio=0.05, include_labels=True)
train_logs_for_isolated_models = generate_logs_with_sessions(num_sessions=40000, anomaly_ratio=0.05, include_labels=False)

# Logs speichern
with open("train_logs.json", "w") as f:
    json.dump(train_logs, f, indent=2)

with open("val_logs.json", "w") as f:
    json.dump(val_logs, f, indent=2)

with open("test_logs.json", "w") as f:
    json.dump(test_logs, f, indent=2)

with open("train_logs_isolated.json", "w") as f:
    json.dump(train_logs_for_isolated_models, f, indent=2)


# Logs laden
with open("train_logs.json") as f:
    logs_train = json.load(f)

with open("val_logs.json") as f:
    logs_val = json.load(f)

with open("test_logs.json") as f:
    logs_test = json.load(f)

with open("train_logs_isolated.json") as f:
    logs_train_isolated = json.load(f)
