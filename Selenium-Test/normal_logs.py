import json
import os
import secrets
import string
import threading
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
token_url_local = os.getenv("token_url_local")

admin_username_local = os.getenv("admin_username_local")
admin_password_local = os.getenv("admin_password_local")

client_secret_aws = os.getenv("client_secret_aws")
client_secret_ubisoft = os.getenv("client_secret_ubisoft")
client_secret_sega = os.getenv("client_secret_sega")
client_secret_nintendo = os.getenv("client_secret_nintendo")

def choose_realm():
    realm = random.choice(["Sega", "Nintendo", "ubisoft", "aws"])

    if realm == "Sega":
        client_two = "megadrive"
        client_secret = client_secret_sega
        with open("user_passwords_sega.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "Nintendo":
        client_two = "wiii"
        client_secret = client_secret_nintendo
        with open("user_passwords_nintendo.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "ubisoft":
        client_two = "ps3"
        client_secret = client_secret_ubisoft
        with open("user_passwords.json", "r") as f:
            user_passwords = json.load(f)

    if realm == "aws":
        client_two = "aws-console"
        client_secret = client_secret_aws
        with open("user_passwords_aws.json", "r") as f:
            user_passwords = json.load(f)

    return realm, client_secret, client_two, user_passwords


def simulate_login(username_now, password_now, realm, client_two, driver):
    login_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/auth?client_id={client_two}&response_type=code&scope=openid&redirect_uri={base_url_local}"
    driver.get(login_url)
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(username_now)
    wait.until(EC.visibility_of_element_located((By.ID, "password"))).send_keys(password_now)
    wait.until(EC.element_to_be_clickable((By.ID, "kc-login"))).click()
    wait.until(EC.url_changes(login_url))


def client_login(client_two, client_secret, realm):
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
    
def simulate_logout(realm, driver):
    logout_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/logout"
    driver.get(logout_url)
    print("Benutzer wurde ausgeloggt.")

def simulate_login_error(username_now, password_now, realm, client_two, driver):
    simulate_login(username_now, "trololololol", realm, client_two, driver)


def generate_random_email():
    name = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    domain = random.choice(["activision.de", "mail.com", "aws.com"])
    return f"{name}@{domain}"

def simulate_profile_update(realm, driver):
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


def simulate_refresh_token(username, password, realm, client_id, client_secret):
    token_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/token"

    # Initial login – um refresh_token zu erhalten
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,  # <-- hier mitgeben
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
            "client_id": client_id,
            "client_secret": client_secret  # <-- hier mitgeben
        }

        refresh_resp = requests.post(token_url, data=refresh_payload)
        if refresh_resp.status_code == 200:
            print("[Token] Refresh erfolgreich.")
        else:
            print("[Token] Refresh fehlgeschlagen:", refresh_resp.text)
    else:
        print("[Token] Initialer Login für Refresh fehlgeschlagen:", response.text)


def simulate_user_session(username, password, realm, client_two, client_secret, driver, min_refresh=10, max_refresh=20):
    try:
        print(f"Starte Session für User: {username}")
        simulate_login(username, password, realm, client_two, driver)

        if random.random() < 0.3:
            print("[Client Login] Versuche Client-Login")
            token = client_login(client_two, client_secret, realm)
            if token:
                print("[Client Login] Erfolgreich")
            else:
                print("[Client Login] Fehlgeschlagen")

        # Erste Wartephase nach Login
        time.sleep(random.uniform(60, 120))  # 1–2 Minuten

        # Refresh Token Loop – realistisch gestreckt
        refresh_count = random.randint(min_refresh, max_refresh)  # z. B. 10–20
        for _ in range(refresh_count):
            simulate_refresh_token(username, password, realm, client_two, client_secret)
            time.sleep(random.uniform(60, 90))  # jede Runde 1–1.5 Min = 10–30 Min

        if random.random() < 0.0001:
            simulate_profile_update(realm, driver)
            time.sleep(random.uniform(60, 90))  # weitere 1–1.5 Min

        if random.random() < 0.05:
            simulate_login_error(username, password, realm, client_two, driver)
            time.sleep(random.uniform(60, 90))  # weitere 1–1.5 Min

        # Logout am Ende
        simulate_logout(realm, driver)
        print(f"Session beendet für User: {username}")

        # Letzte Pause, um auf ca. 30 Minuten zu kommen
        time.sleep(random.uniform(60, 120))  # 1–2 Minuten

    finally:
        driver.quit()



def run_parallel_sessions(total_sessions=15):
    threads = []
    last_user = None
    
    for i in range(total_sessions):
        realm, client_secret, client_two, user_passwords = choose_realm()
        
        while True:
            random_user = random.choice(user_passwords)
            if random_user != last_user:
                break
        last_user = random_user
        
        username_now = random_user["username"]
        password_now = random_user["password"]

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        t = threading.Thread(target=simulate_user_session, args=(username_now, password_now, realm, client_two, client_secret, driver))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

run_parallel_sessions(15)

driver.quit()
print("Test abgeschlossen.")
