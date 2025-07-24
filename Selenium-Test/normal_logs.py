import json
import os
import secrets
import string
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

load_dotenv()

base_url_local = os.getenv("base_url_local")
admin_url_local = os.getenv("admin_url_local")

admin_username_local = os.getenv("admin_username_local")
admin_password_local = os.getenv("admin_password_local")

def choose_realm():
    realm = random.choice(["Sega", "Nintendo", "ubisoft", "aws"])

    if realm == "Sega":
        client_two = "megadrive"
        client_secret = "9reshZStMOA5bt0bJzXt3Q5P67sy5x5p"
        with open("user_passwords_sega.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "Nintendo":
        client_two = "wiii"
        client_secret = "j9sIIjLlZg0DazfTHNCiCev4WoEVHAbq"
        with open("user_passwords_nintendo.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "ubisoft":
        client_two = "ps3"
        client_secret = "9WXaMXTUEM5r5J8j5YBtPEwVsxiiKjTs"
        with open("user_passwords.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "aws":
        client_two = "aws-console"
        client_secret = "jVRUonJKG3iuuuzPtGzX2iei8L8vSlkT"
        with open("user_passwords_aws.json", "r") as f:
            user_passwords = json.load(f)

    return realm, client_secret, client_two, user_passwords


def simulate_login(username_now, password_now, realm, client_two):
    login_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/auth?client_id={client_two}&response_type=code&scope=openid&redirect_uri={base_url_local}"
    driver.get(login_url)
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(username_now)
    wait.until(EC.visibility_of_element_located((By.ID, "password"))).send_keys(password_now)
    wait.until(EC.element_to_be_clickable((By.ID, "kc-login"))).click()
    wait.until(EC.url_changes(login_url))


def client_login(client_two, client_secret):
    token_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_two,
        "client_secret": client_secret
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        token_data = response.json()
        print("[Client Login] Access Token erhalten.")
        return token_data["access_token"]
    else:
        print("[Client Login] Fehler beim Abrufen des Tokens!")
        print(response.status_code, response.text)
        return None
    
def simulate_logout(realm):
    logout_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/logout"
    driver.get(logout_url)
    print("Benutzer wurde ausgeloggt.")

def simulate_login_error(username_now, password_now, realm, client_two):
    simulate_login(username_now, "trololololol", realm, client_two)

def simulate_admin_actions(realm):
    try:
        driver.get(f"{base_url_local}/admin/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(admin_username_local)
        driver.find_element(By.ID, "password").send_keys(admin_password_local)
        driver.find_element(By.ID, "kc-login").click()
        time.sleep(3)

        driver.get(f"{base_url_local}/admin/master/console/#/realms/{realm}/users")
        time.sleep(4)

        user_links = driver.find_elements(By.CSS_SELECTOR, "a.kc-user-link")
        if not user_links:
            print("[Admin] Keine Benutzer gefunden.")
            return

        selected_user = random.choice(user_links)
        username = selected_user.text
        selected_user.click()
        time.sleep(2)

        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        new_email = generate_random_email()
        email_input.clear()
        email_input.send_keys(new_email)

        save_button = driver.find_element(By.XPATH, "//button[.='Save']")
        save_button.click()
        time.sleep(2)

        print(f"[Admin] E-Mail von Benutzer '{username}' geändert zu: {new_email}")

    except Exception as e:
        print("[Admin] Fehler beim Simulieren einer Admin-Aktion:", e)


def generate_random_email():
    name = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    domain = random.choice(["activision.de", "mail.com", "aws.com"])
    return f"{name}@{domain}"

def simulate_profile_update(realm):
    driver.get(f"{base_url_local}/realms/{realm}/account")
    time.sleep(2)

    try:
        # Warte auf das E-Mail-Feld
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))

        new_email = generate_random_email()
        email_input.clear()
        email_input.send_keys(new_email)

        # Speichern-Button klicken
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()

        print(f"[Profilupdate] Neue E-Mail gesetzt: {new_email}")
    except Exception as e:
        print("[Profilupdate] Fehler beim Aktualisieren:", e)

def simulate_refresh_token(username, password, realm, client_id):
    token_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/token"

    # Initial login – um refresh_token zu erhalten
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password
    }

    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")

        # Jetzt Refresh durchführen
        refresh_payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id
        }

        refresh_resp = requests.post(token_url, data=refresh_payload)
        if refresh_resp.status_code == 200:
            print("[Token] Refresh erfolgreich.")
        else:
            print("[Token] Refresh fehlgeschlagen:", refresh_resp.text)
    else:
        print("[Token] Initialer Login für Refresh fehlgeschlagen.")

def assign_realm_role_to_user(admin_token, realm, user_id, role_name):
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 1. Rolle abrufen
    role_url = f"{base_url_local}/admin/realms/{realm}/roles/{role_name}"
    role_resp = requests.get(role_url, headers=headers)
    role_resp.raise_for_status()
    role = role_resp.json()

    # 2. Rolle zuweisen
    assign_url = f"{base_url_local}/admin/realms/{realm}/users/{user_id}/role-mappings/realm"
    assign_resp = requests.post(assign_url, headers=headers, json=[role])
    
    if assign_resp.status_code == 204:
        print(f"[Admin] Rolle '{role_name}' zugewiesen an Benutzer {user_id}")
    else:
        print("[Admin] Rollenzuweisung fehlgeschlagen:", assign_resp.text)

def assign_client_role_to_user(admin_token, realm, client_id, user_id, role_name):
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    # 1. Hole Client UUID
    clients_url = f"{base_url_local}/admin/realms/{realm}/clients"
    clients_resp = requests.get(clients_url, headers=headers)
    clients_resp.raise_for_status()
    clients = clients_resp.json()
    client_uuid = next(c["id"] for c in clients if c["clientId"] == client_id)

    # 2. Hole die Rolle aus diesem Client
    role_url = f"{base_url_local}/admin/realms/{realm}/clients/{client_uuid}/roles/{role_name}"
    role_resp = requests.get(role_url, headers=headers)
    role = role_resp.json()

    # 3. Rolle zuweisen
    assign_url = f"{base_url_local}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_uuid}"
    assign_resp = requests.post(assign_url, headers=headers, json=[role])

    if assign_resp.status_code == 204:
        print(f"[Admin] Clientrolle '{role_name}' zugewiesen an Benutzer {user_id}")
    else:
        print("[Admin] Clientrollenzuweisung fehlgeschlagen:", assign_resp.text)


last_user = None

for i in range(1000):
    realm, client_secret, client_two, user_passwords = choose_realm()
    # Neu starten
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Benutzer wählen
    while True:
        random_user = random.choice(user_passwords)
        if random_user != last_user:
            break

    username_now = random_user["username"]
    password_now = random_user["password"]
    last_user = random_user
    print(f"[{i}] Login mit Benutzer: {username_now}")

    simulate_login(username_now, password_now, realm, client_two)
    time.sleep(random.randint(3, 7))

    if random.random() < 0.05:
        simulate_login_error(username_now, password_now, realm, client_two)
        time.sleep(5)

    if random.random() < 0.2:
        client_login(client_two, client_secret)
        time.sleep(5)

    if random.random() < 0.01:
        simulate_admin_actions(realm)
        time.sleep(5)

    if random.random() < 0.05:
        simulate_logout(realm)
        time.sleep(2)

    if random.random() < 0.01:
        simulate_profile_update(realm)
        time.sleep(2)


    driver.quit()
    time.sleep(1)

driver.quit()
print("Test abgeschlossen.")
