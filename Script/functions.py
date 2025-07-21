import random
import uuid
import pytz
from datetime import datetime, timedelta
from constants import clients, normal_realms, user_pool

tz = pytz.timezone('Europe/Berlin')

normal_hours = list(range(8, 19))
anomaly_hours = list(range(0, 6))

normal_hour = random.choice(normal_hours)
anomaly_hour = random.choice(anomaly_hours)

minute = random.randint(0, 59)
second = random.randint(0, 59)

timestamp = datetime.now(tz).replace(hour=normal_hour, minute=minute, second=second, microsecond=0) - timedelta(days=random.randint(0, 5))
timestamp_anomaly = datetime.now(tz).replace(hour=anomaly_hour, minute=minute, second=second, microsecond=0) - timedelta(days=random.randint(0, 5))

last_session_times = {}
generated_log_ids = set()
user_realm_map = {user_id: random.choice(normal_realms) for user_id in user_pool}

allowed_client_event_map = {
    client: ["LOGIN", "CODE_TO_TOKEN", "REFRESH_TOKEN", "CLIENT_LOGIN"] for client in clients
}

ip = f"{random.randint(10, 100)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

def add_contextual_event_details(log, clients, user_id, context):
    event_type = log.get("type")
    
    # Flache Detailfelder direkt im Log speichern
    log["log_level"] = random.choice(["info", "debug", "trace"]) if "ERROR" not in event_type else random.choice(["debug", "error", "fatal"])
    log["auth_type"] = context.get("protocol", "openid-connect")
    log["connection"] = context.get("connection", "internet")
    log["scope"] = context.get("scope", "openid profile")
    log["grant_type"] = context.get("grant_type", "authorization_code")
    log["refresh_token_id"] = str(uuid.uuid4())
    log["code_id"] = str(uuid.uuid4())

    if "ERROR" in event_type:
        log["username"] = user_id
        log["ipAdress"] = ip

    return log

def assign_realm_and_validate_session(log, user_id):
    # Realm zuweisen
    realm = user_realm_map.get(user_id, random.choice(normal_realms))
    log["realmId"] = realm
    log["realmName"] = realm

    # Gültige ClientId prüfen
    client_id = log.get("clientId")
    event_type = log.get("type")
    allowed_events = allowed_client_event_map.get(client_id, [])
    if event_type not in allowed_events:
        valid_clients = [c for c, events in allowed_client_event_map.items() if event_type in events]
        log["clientId"] = random.choice(valid_clients) if valid_clients else clients[0]

    # Timestamp-Anpassung
    timestamp = datetime.fromisoformat(log["timestamp"])
    last_time = last_session_times.get(user_id)
    if last_time and (timestamp - last_time).total_seconds() < 3600:
        timestamp = last_time + timedelta(seconds=3600)
        log["timestamp"] = timestamp.isoformat()
    last_session_times[user_id] = timestamp

    # sessionId sicher in String-Format
    session_id = log.get("sessionId")
    if isinstance(session_id, list):
        session_id = "_".join(session_id)
    elif isinstance(session_id, uuid.UUID):
        session_id = str(session_id)
    log["sessionId"] = session_id

    # Hash erstellen für Duplikatsprüfung
    log_hash = (log.get("userId"), log.get("timestamp"), log.get("type"), log.get("clientId"), session_id)
    if log_hash in generated_log_ids:
        new_time = timestamp + timedelta(seconds=random.randint(1, 10))
        log["timestamp"] = new_time.isoformat()
        log_hash = (log.get("userId"), log["timestamp"], log.get("type"), log.get("clientId"), session_id)
        generated_log_ids.add(log_hash)
    else:
        generated_log_ids.add(log_hash)

    return log
