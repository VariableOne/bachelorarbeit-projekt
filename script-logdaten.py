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


admin_operations = ["CREATE", "UPDATE", "DELETE", "GET"]
resource_types = ["users", "clients", "roles", "groups", "authentication"]

tz = pytz.timezone('Europe/Berlin')
#with open("names.json") as f:
#    names = json.load(f)
#    user_pool = names[:50]

names = [
        'Anna', 'Bob', 'Carlos', 'Diana', 'Elena', 'Faisal', 'Gina', 'Hiroshi', 'Isabel',
        'Jamal', 'Klara', 'Luca', 'Maya', 'Nina', 'Omar', 'Priya', 'Quentin', 'Rina',
        'Sofia', 'Tom', 'Usha', 'Victor', 'Wei', 'Yara', 'Zane', 'Ivan', 'Zara',
        'Mikhail', 'Layla', 'Rashid', 'Svetlana', 'Oleg', 'Nadia', 'Kenji', 'Farah'
    ]

user_pool = names[:25]

normal_hours = list(range(8, 19))
anomaly_hours = list(range(0, 6))

normal_hour = random.choice(normal_hours)
anomaly_hour = random.choice(anomaly_hours)

minute = random.randint(0, 59)
second = random.randint(0, 59)

timestamp = datetime.now(tz).replace(hour=normal_hour, minute=minute, second=second, microsecond=0) - timedelta(days=random.randint(0, 5))
timestamp_anomaly = datetime.now(tz).replace(hour=anomaly_hour, minute=minute, second=second, microsecond=0) - timedelta(days=random.randint(0, 5))

def add_contextual_event_details(log, clients):
    event_type = log.get("type", "")
    user_id = log.get("userId", "")
    details = {}
    error = None

    if event_type in ["LOGIN", "LOGIN_ERROR", "REGISTER", "REGISTER_ERROR"]:
        details["auth_method"] = random.choice(["openid-connect", "saml"])
        details["auth_type"] = random.choice(["code", "implicit"])
        if "error" in event_type:
            error = random.choice(["invalid_credentials", "user_not_found"])

    elif event_type in ["VERIFY_EMAIL", "FORGOT_PASSWORD", "RESET_PASSWORD"]:
        details["email"] = f"user{user_id}@{random.choice(normal_realms)}.com"

    elif event_type in ["IMPERSONATE", "IMPERSONATE_ERROR"]:
        details["impersonator"] = f"{user_id}"
        if "error" in event_type:
            error = random.choice(["impersonation_denied"])

    elif event_type == "CODE_TO_TOKEN":
        details["client_auth_method"] = random.choice(["client_secret_basic", "client_secret_post"])

    elif event_type == "CODE_TO_TOKEN_ERROR":
        details["client_auth_method"] = random.choice(["client_secret_basic", "client_secret_post"])
        error = random.choice(["invalid_grant", "unauthorized_client"])

    elif event_type in ["CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH"]:
        details["client_id"] = random.choice(clients)
        if "error" in event_type:
            error = random.choice(["invalid_client", "unauthorized_client"])

    elif event_type == "BRUTE_FORCE_ERROR":
        details["username"] = f"{user_id}"
        error = "brute_force_detected"

    elif event_type == "BRUTE_FORCE_RESET":
        details["username"] = f"{user_id}"

    elif event_type == "REVOKE_GRANT":
        details["client_id"] = random.choice(clients)

    log["details"] = details
    if error:
        log["error"] = error

    return log


def add_admin_roles_and_metadata(log):
    # 10% Chance, dass überhaupt versucht wird, einen Admin-Log zu machen
    admin_users_per_realm = assign_admins_to_realms(normal_realms)
    is_admin = random.random() < 0.1

    user_id = log["userId"]
    realm = log["realmName"]
    real_admin = admin_users_per_realm.get(realm)

    if is_admin and user_id == real_admin:
        roles = ["admin"]
        admin_only_roles = [
            "security-admin-console",
            "realm-management",
            "manage-users",
            "manage-clients",
            "manage-events",
            "manage-realm",
            "view-users",
            "admin-cli"
        ]
        roles += random.sample(admin_only_roles, k=random.randint(2, 5))
        log["roles"] = roles

        if "operationType" in log:
            log.setdefault("details", {})["operationType"] = log["operationType"]
        else:
            # Normale User-Rollen (nicht admin)
          normal_roles = [r for r in realm_roles if r != "admin"]
          log["roles"] = random.sample(normal_roles, k=random.randint(1, 3))

    return log



def clean_irrelevant_fields(log):
    event_type = log.get("type", "")

    login_related_events = [
        "LOGIN", "LOGIN_ERROR", "REGISTER", "REGISTER_ERROR",
        "CODE_TO_TOKEN", "CODE_TO_TOKEN_ERROR",
        "CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH"
    ]
    token_related_events = [
        "CODE_TO_TOKEN", "CODE_TO_TOKEN_ERROR",
        "CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH"
    ]

    # auth-Attribute nur bei login-/token-events
    if event_type not in login_related_events:
        for key in ["authMethod", "authType", "resourceType", "resourcePath"]:
            log.get("details", {}).pop(key, None)

    # Rollen nur bei token-relevanten Events
    if event_type not in token_related_events:
        log.pop("roles", None)

    return log



def assign_admins_to_realms(realms):
    admin_users = {}
    used_names = set()
    for realm in realms:
        while True:
            candidate = f"admin_{random.randint(1, 100)}"
            if candidate not in used_names:
                admin_users[realm] = candidate
                used_names.add(candidate)
                break
    return admin_users



def generate_noise_session(user_id, include_labels):
    logs = []
    sequence = [
        random.choice(["LOGIN_ERROR", "FORGOT_PASSWORD", "UPDATE_PROFILE", "RESET_PASSWORD", "CODE_TO_TOKEN_ERROR"])
        for _ in range(random.randint(2, 4))
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
            "error": None,
            "authMethod": random.choice(protocols),
            "authType": "code",
            "operationType": None,
            "resourceType": random.choice(resource_types),
            "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
        }
        log = add_contextual_event_details(log, clients)
        log = clean_irrelevant_fields(log)
        if include_labels:
            log["label"] = 0  # Noise ist nicht Angriff
        logs.append(log)

    return logs

def generate_normal_user_log(user_id, include_labels):
    logs = []

    # Haupt-Log (Login etc.)
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
        "error": None,
        "authMethod": random.choice(protocols),
        "authType": "code",
        "resourceType": random.choice(resource_types),
        "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000,9999)}",
    }
    log = add_contextual_event_details(log, clients)
    log = add_admin_roles_and_metadata(log)
    log = clean_irrelevant_fields(log)

    if include_labels:
        log["label"] = 0
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


def generate_brute_force_session(user_id, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    client = 'login-app'
    
    # Viele fehlgeschlagene Login-Versuche
    for i in range(random.randint(5, 15)):
        log = {
            "timestamp":(timestamp_anomaly + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "warn",
            "category": "org.keycloak.events",
            "type": "LOGIN_ERROR",
            "realmId": realm,
            "realmName": realm_name,
            "clientId": client,
            "userId": user_id,
            "sessionId": f"session_{random.randint(1000,9999)}",
            "ipAddress": f"{get_unusual_ip()}",
            "error": "invalid_credentials",
            "authMethod": "openid-connect",
            "authType": "password",
            "operationType": None,
            "resourceType": None,
            "resourcePath": None,
        }
        if include_labels:
            log["label"] = 1
        logs.append(log)
    
    return logs


def generate_privilege_exploitation_session(user_id, timestamp_anomaly, include_labels):
    logs = []
    realm = 'master'
    realm_name = 'master'
    admin_client = 'admin-cli'
    escalated_roles = ['admin', 'realm-admin', 'manage-users']

    anomaly_event_types = [
        "LOGIN", "IMPERSONATE", "IMPERSONATE_ERROR"
    ]
    
    number_of_events = random.randint(3, 7)

    for _ in range(number_of_events):
        event = random.choice(anomaly_event_types)
        log = {
            "timestamp": (timestamp_anomaly + timedelta(seconds=random.randint(1, 60000))).isoformat(),
            "log_level": "info",
            "category": "org.keycloak.events",
            "type": event["type"],
            "realmId": realm,
            "realmName": realm_name,
            "clientId": event["clientId"],
            "userId": user_id,
            "sessionId": f"session_{random.randint(1000, 9999)}",
            "ipAddress": get_unusual_ip(),
            "error": None,
            #"roles": escalated_roles,
            "authMethod": "openid-connect",
            "authType": "code",
            "operationType": None,
            "resourceType": random.choice(resource_types),
            "resourcePath": f"{random.choice(['users', 'clients'])}/{random.randint(1000, 9999)}",
        }
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)

        if include_labels:
            log["label"] = 1
        logs.append(log)
        
    return logs


def generate_sabotage_session(user_id, timestamp_anomaly, include_labels):
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

    number_of_events = random.randint(3, 7)  # wie viele Ereignisse in der Session

    for i in range(number_of_events):
        event_type = random.choice(sabotage_events)
        log = {
            "timestamp": (timestamp_anomaly + timedelta(seconds=i * random.randint(10, 60))).isoformat(),
            "log_level": "info",
            "category": "org.keycloak.events",
            "type": event_type,
            "realmId": realm,
            "realmName": realm_name,
            "clientId": admin_client,
            "userId": user_id,
            "sessionId": f"session_{random.randint(1000,9999)}",
            "ipAddress": get_unusual_ip(),
            "error": None,
            "authMethod": "openid-connect",
            "authType": "code",
            "operationType": random.choice('UPDATE', 'DELETE', 'GET'),
        }
        log = add_contextual_event_details(log, clients)
        log = add_admin_roles_and_metadata(log)
        log = clean_irrelevant_fields(log)

        if include_labels:
            log["label"] = 1
        logs.append(log)
    return logs


def generate_logs_with_sessions(num_sessions, anomaly_probability, include_labels):
    logs = []

    for _ in range(num_sessions):
        if random.random() < anomaly_probability:
            # Angriffssession mit 10 % Wahrscheinlichkeit
            attack_type = random.choice(['privilege_exploitation'])
            user_id = random.choice(user_pool)

            if attack_type == 'privilege_exploitation':
                logs.extend(generate_privilege_exploitation_session(
                    user_id=user_id,
                    include_labels=include_labels
                ))
        else:
            # Normale Logs
            user_id = random.choice(user_pool)
            logs.extend(generate_normal_user_log(
                user_id=user_id,
                include_labels=include_labels
            ))

       # base_time += timedelta(seconds=random.choice(1, 60000))

    #random.shuffle(logs)
    logs.sort(key=lambda x: x['timestamp'])
    return logs


train_logs = generate_logs_with_sessions(num_sessions=7500, anomaly_probability=0.0, include_labels=False)
val_logs   = generate_logs_with_sessions(num_sessions=1250, anomaly_probability=0.05, include_labels=True)
test_logs  = generate_logs_with_sessions(num_sessions=1250, anomaly_probability=0.05, include_labels=True)
train_logs_for_isolated_models = generate_logs_with_sessions(num_sessions=7500, anomaly_probability=0.2, include_labels=False)

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
