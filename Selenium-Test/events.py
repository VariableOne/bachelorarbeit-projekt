import os
import requests
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

token_url_local = os.getenv("token_url_local")
event_url_local = os.getenv("event_url_local")

# Client-Daten für die verschiedenen Realms (aktuell leer)
clients = {
    "Sega": {"client_id": "Sega", "client_secret": ""},
    "Nintendo": {"client_id": "Nintendo", "client_secret": ""},
    "Ubisoft": {"client_id": "Ubisoft", "client_secret": ""},
    "AWS": {"client_id": "AWS", "client_secret": ""}
}

def get_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    resp = requests.post(token_url_local, data=data)
    resp.raise_for_status()
    return resp.json()['access_token']

def clean_logs(events):
    cleaned = []
    for e in events:
        e.pop("ipAddress", None)  # Entfernt die IP-Adresse, falls vorhanden
        cleaned.append(e)
    return cleaned

def save_events_to_file(events):
    filename = datetime.now().strftime("normallogs.jsonl")
    with open(filename, "w") as f:  # "w" damit die Datei neu geschrieben wird
        for event in events:
            f.write(json.dumps(event) + "\n")
    print(f"Events gespeichert in {filename}")

def get_all_events(token):
    headers = {'authorization': f'bearer {token}'}
    params = {'max': 3000}
    resp = requests.get(event_url_local, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    all_events = []
    for realm, creds in clients.items():
        print(f"Hole Events für Realm {realm}...")
        # token holen, falls client_secret leer ist, überspringen wir den Realm
        if not creds['client_secret']:
            print(f"Kein client_secret für {realm}, Realm übersprungen.")
            continue
        token = get_token(creds['client_id'], creds['client_secret'])
        events = get_all_events(token)
        cleaned = clean_logs(events)
        # Optional: Realm als Feld hinzufügen, um Herkunft zu erkennen
        for event in cleaned:
            event['realm'] = realm
        all_events.extend(cleaned)

    # Sortiere alle Events nach Zeitstempel (angenommen das Feld heißt "timestamp")
    # Falls das Feld anders heißt, passe es entsprechend an
    all_events.sort(key=lambda x: x.get('timestamp', ''))

    save_events_to_file(all_events)