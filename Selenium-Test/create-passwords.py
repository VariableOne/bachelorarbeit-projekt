import requests
import string
import secrets

token_url = "http://localhost:8080/realms/aws/protocol/openid-connect/token"
client_id = "aws-console"
client_secret = "jVRUonJKG3iuuuzPtGzX2iei8L8vSlkT"

def get_admin_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

base_url = "http://localhost:8080"
realm = "aws"

def get_all_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    users = []
    first = 0
    max_results = 50
    while True:
        params = {"first": first, "max": max_results}
        resp = requests.get(f"{base_url}/admin/realms/{realm}/users", headers=headers, params=params)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        users.extend(batch)
        first += max_results
    return users

def set_password(token, user_id, new_password):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "password",
        "value": new_password,
        "temporary": False
    }
    resp = requests.put(f"{base_url}/admin/realms/{realm}/users/{user_id}/reset-password", headers=headers, json=payload)
    resp.raise_for_status()

import json

def save_user_passwords(user_passwords, filename="user_passwords_aws.json"):
    # Umwandeln in Liste von Dictionaries
    data = [{"username": u, "password": p} for u, p in user_passwords]

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)  # schön formatiert speichern


def main():
    token = get_admin_token()
    users = get_all_users(token)

    user_passwords_nintendo = []

    for user in users:
        username = user['username']
        user_id = user['id']
        pwd = generate_password()
        set_password(token, user_id, pwd)
        user_passwords_nintendo.append((username, pwd))
        print(f"Passwort für {username} gesetzt.")

    print("\nUser und neue Passwörter:")
    for u, p in user_passwords_nintendo:
        print(f"{u}: {p}")

    # Speichere die Daten als JSON ab
    save_user_passwords(user_passwords_nintendo)

if __name__ == "__main__":
    main()
