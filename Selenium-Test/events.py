import os
import requests
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

token_url_local = os.getenv("token_url_local")
event_url_local = os.getenv("event_url_local")

def get_token():
    data = {
        'client_id': "Sega",
        'client_secret': "9reshZStMOA5bt0bJzXt3Q5P67sy5x5p",
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
    with open(filename, "a") as f:
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
    token = get_token()
    events = get_all_events(token)
    cleaned_events = clean_logs(events)
    save_events_to_file(cleaned_events)