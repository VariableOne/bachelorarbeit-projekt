import os
import random
import requests
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

token_url_local = os.getenv("token_url_local")
event_url_local = os.getenv("event_url_local")

client_secret_aws = os.getenv("client_secret_aws")
client_secret_ubisoft = os.getenv("client_secret_ubisoft")
client_secret_sega = os.getenv("client_secret_sega")
client_secret_nintendo = os.getenv("client_secret_nintendo")

clients = {
    "Sega": {"client_id": "megadrive", "client_secret": client_secret_sega},
    "Nintendo": {"client_id": "wiii", "client_secret": client_secret_nintendo},
    "ubisoft": {"client_id": "ps3", "client_secret": client_secret_ubisoft},
    "aws": {"client_id": "aws-console", "client_secret": client_secret_aws}
}

def get_admin_events(token, realm):
    headers = {'authorization': f'bearer {token}'}
    params = {'max': 10000}
    resp = requests.get(f"http://localhost:8080/admin/realms/{realm}/admin-events", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def get_token(client_id, client_secret, realm):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    resp = requests.post(f"http://localhost:8080/realms/{realm}/protocol/openid-connect/token", data=data)
    resp.raise_for_status()
    return resp.json()['access_token']

def remove_ip_recursive(obj):
    if isinstance(obj, dict):
        # Entferne 'ipAddress' im aktuellen dict
        obj.pop('ipAddress', None)
        # Gehe rekursiv alle Werte durch
        for key, value in obj.items():
            remove_ip_recursive(value)
    elif isinstance(obj, list):
        for item in obj:
            remove_ip_recursive(item)

def clean_logs(events):
    for e in events:
        remove_ip_recursive(e)
    return events

def save_events_to_file(events):
    filename = datetime.now().strftime("getted_normallogs.jsonl")
    with open(filename, "w") as f:  # "w" damit die Datei neu geschrieben wird
        for event in events:
            f.write(json.dumps(event) + "\n")
    print(f"Events gespeichert in {filename}")

def get_all_events(token, realm):
    headers = {'authorization': f'bearer {token}'}
    params = {'max': 50000}
    resp = requests.get(f"http://localhost:8080/admin/realms/{realm}/events", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
        all_user_events = []
        all_admin_events = []

        for realm, creds in clients.items():
            print(f"Hole Events für Realm {realm}...")
            if not creds['client_secret']:
                print(f"Kein client_secret für {realm}, Realm übersprungen.")
                continue
            token = get_token(creds['client_id'], creds['client_secret'], realm)

            # User-Events holen
            user_events = get_all_events(token, realm)
            cleaned_user_events = clean_logs(user_events)
            all_user_events.extend(cleaned_user_events)

            admin_events = get_admin_events(token, realm)
            cleaned_admin_events = clean_logs(admin_events)
            all_admin_events.extend(cleaned_admin_events)

        # Kombinieren und sortieren
        all_events = all_user_events + all_admin_events
        all_events.sort(key=lambda x: (x.get('time', 0), random.random()))
        save_events_to_file(all_events)

