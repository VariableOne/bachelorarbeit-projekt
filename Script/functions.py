import random
from datetime import datetime, timedelta
import pytz
import json
from datetime import datetime, time, timedelta
from constants import clients, connections, realm_roles, normal_realms, user_pool, admin_operations

tz = pytz.timezone('Europe/Berlin')

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
    details = {}
    error = None

    # 4: Details nur bei passenden Events
    if event_type in ["LOGIN", "LOGIN_ERROR", "REGISTER", "REGISTER_ERROR"]:
        details["auth_method"] = random.choice(["openid-connect", "saml"])
        details["auth_type"] = random.choice(["code", "implicit"])
        details["connection"] = random.choice(connections)

        if "error" in event_type:
            error = random.choice(["invalid_credentials", "user_not_found"])

    elif event_type in ["IMPERSONATE", "IMPERSONATE_ERROR"]:
        details["was_impersonation"] = 1
        if "error" in event_type:
            error = "impersonation_denied"

    if event_type in ["CODE_TO_TOKEN", "CODE_TO_TOKEN_ERROR"]:
        details["client_auth_method"] = random.choice(["client_secret_basic", "client_secret_post"])
        if "error" in event_type:
            error = random.choice(["invalid_grant", "unauthorized_client"])

    if event_type in ["CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH", "REVOKE_GRANT"]:
        details["client_id"] = random.choice(clients)
        if "error" in event_type:
            error = random.choice(["invalid_client", "unauthorized_client"])

    if event_type == "BRUTE_FORCE_ERROR":
        details["brute_force_detected"] = 1
        error = "brute_force"

    if event_type in ["LOGIN", "CODE_TO_TOKEN", "TOKEN_REFRESH", "CLIENT_LOGIN"]:
        details["client_scopes"] = [
            "profile", "email",
            random.choice(["roles", "offline_access", "web-origins", "microprofile-jwt"])
        ]

    auth_method = log.get("authMethod")
    roles = log.get("roles", [])
    if auth_method == "admin-cli" and "admin" not in roles:
        roles.append("admin")
        log["roles"] = roles

    allowed_errors = {
        "LOGIN_ERROR": ["invalid_credentials", "user_not_found"],
        "IMPERSONATE_ERROR": ["impersonation_denied"],
        "CODE_TO_TOKEN_ERROR": ["invalid_grant", "unauthorized_client"],
        "CLIENT_LOGIN_ERROR": ["invalid_client", "unauthorized_client"],
        "BRUTE_FORCE_ERROR": ["brute_force"]
    }
    if error and error not in allowed_errors.get(event_type, []):
        error = "none"

    log["details"] = details
    log["error"] = error if error else "none"

    return log


def label_if_multiple_admins(logs):
    admin_user_ids = set()

    for log in logs:
        if "admin" in log.get("roles", []):
            admin_user_ids.add(log["userId"])

    if len(admin_user_ids) > 1:
        return 1  # Verstoß
    else:
        return 0  # Kein Verstoß



def add_admin_roles_and_metadata(log):
    # 10% Chance, dass überhaupt versucht wird, einen Admin-Log zu machen
    is_admin = random.random() < 0.1

    user_id = log["userId"]
    realm = log["realmName"]

    if is_admin and user_id == "admin":
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

        operation = log.get("operationType")
        if operation in admin_operations:
            if "roles" not in log or "admin" not in log["roles"]:
                # Rollen setzen oder Log verwerfen (je nach Logik)
                log["roles"] = ["admin"]
        
    return log

last_session_times = {}
generated_log_ids = set()

user_realm_map = {user_id: random.choice(normal_realms) for user_id in user_pool}

allowed_client_event_map = {
    client: ["LOGIN", "CODE_TO_TOKEN", "TOKEN_REFRESH", "CLIENT_LOGIN", "GET"] for client in clients
}

def assign_realm_and_validate_session(log, user_id):
    realm = user_realm_map.get(user_id, random.choice(normal_realms))
    log["realmId"] = realm
    log["realmName"] = realm

    client_id = log.get("clientId")
    event_type = log.get("type")
    allowed_events = allowed_client_event_map.get(client_id, [])
    if event_type not in allowed_events:
        valid_clients = [c for c, events in allowed_client_event_map.items() if event_type in events]
        if valid_clients:
            log["clientId"] = random.choice(valid_clients)
        else:
            log["clientId"] = clients[0]

    # Session-Zeit prüfen (5)
    timestamp = datetime.fromisoformat(log["timestamp"])
    last_time = last_session_times.get(user_id)
    if last_time and (timestamp - last_time).total_seconds() < 3600:
        # Wenn zu nah an letzter Session, Verschiebe Zeit +3600 sec
        timestamp = last_time + timedelta(seconds=3600)
        log["timestamp"] = timestamp.isoformat()
    last_session_times[user_id] = timestamp

    # Duplikate vermeiden (6)
    # Erzeuge einfachen Hash aus userId, timestamp, type, clientId, sessionId
    log_hash = (log.get("userId"), log.get("timestamp"), log.get("type"), log.get("clientId"), log.get("sessionId"))
    if log_hash in generated_log_ids:
        # Füge zufällige Sekunde hinzu um Duplikat zu vermeiden
        new_time = timestamp + timedelta(seconds=random.randint(1, 10))
        log["timestamp"] = new_time.isoformat()
        generated_log_ids.add((log.get("userId"), log.get("timestamp"), log.get("type"), log.get("clientId"), log.get("sessionId")))
    else:
        generated_log_ids.add(log_hash)

    return log



def clean_irrelevant_fields(log):
    event_type = log.get("type", "")

    token_related_events = [
        "CODE_TO_TOKEN", "CODE_TO_TOKEN_ERROR",
        "CLIENT_LOGIN", "CLIENT_LOGIN_ERROR", "TOKEN_REFRESH"
    ]

    if event_type not in token_related_events:
        log.pop("roles", None)

    return log


