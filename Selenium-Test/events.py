import os
import requests
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

client_id_local = os.getenv("client_id_local")
client_secret_local = os.getenv("client_secret_local")
token_url_local = os.getenv("token_url_local")
event_url_local = os.getenv("event_url_local")

def get_token():
    data = {
        'client_id': client_id_local,
        'client_secret': client_secret_local,
        'grant_type': 'client_credentials'
    }
    resp = requests.post(token_url_local, data=data)
    resp.raise_for_status()
    return resp.json()['access_token']

def get_all_events(token):
    headers = {'authorization': f'bearer {token}'}
    resp = requests.get(event_url_local, headers=headers)
    resp.raise_for_status()
    return resp.json()

def save_events_to_file(events):
    filename = datetime.now().strftime("attacks.jsonl")
    with open(filename, "a") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    print(f"events gespeichert in {filename}")

if __name__ == "__main__":
    token = get_token()
    events = get_all_events(token)
    save_events_to_file(events)