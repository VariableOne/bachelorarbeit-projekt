import json
import os
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

base_url_local = os.getenv("base_url_local")
admin_url_local = os.getenv("admin_url_local")

client_secret_aws = os.getenv("client_secret_aws")
client_secret_ubisoft = os.getenv("client_secret_ubisoft")
client_secret_sega = os.getenv("client_secret_sega")
client_secret_nintendo = os.getenv("client_secret_nintendo")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

def choose_realm():
    realm = random.choice(["Sega", "Nintendo", "ubisoft", "aws"])

    if realm == "Sega":
        client_id = "megadrive"
        client_secret = client_secret_sega
        with open("user_passwords_sega.json", "r") as f:
            user_passwords = json.load(f)

    elif realm == "Nintendo":
        client_id = "wiii"
        client_secret = client_secret_nintendo
        with open("user_passwords_nintendo.json", "r") as f:
            user_passwords = json.load(f)

    elif realm == "ubisoft":
        client_id = "ps3"
        client_secret = client_secret_ubisoft
        with open("user_passwords.json", "r") as f:
            user_passwords = json.load(f)

    elif realm == "aws":
        client_id = "aws-console"
        client_secret = client_secret_aws
        with open("user_passwords_aws.json", "r") as f:
            user_passwords = json.load(f)

    else:
        raise ValueError("Unbekannter Realm")

    return realm, client_secret, client_id, user_passwords

def get_token(client_secret, client_id, realm):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    resp = requests.post(f"{base_url_local}/realms/{realm}/protocol/openid-connect/token", data=data)
    resp.raise_for_status()
    token = resp.json()['access_token']
    return token

def get_login_url(realm, client_id):
    return (
        f"{base_url_local}/realms/{realm}/protocol/openid-connect/auth"
        f"?client_id={client_id}&redirect_uri={base_url_local}&response_type=code"
    )

# def test_privilege_escalation():
#     realm, client_secret, client_id, user_passwords = choose_realm()
#     user = random.choice(user_passwords)
#     user_username = user["username"]
#     user_password = user["password"]

#     # Log in und hole Token mit Benutzer
#     data = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'grant_type': 'password',
#         'username': user_username,
#         'password': user_password
#     }

#     token_resp = requests.post(
#         f"http://localhost:8080/realms/{realm}/protocol/openid-connect/token",
#         data=data
#     )

#     if token_resp.status_code != 200:
#         print(f"[{realm}] 🔴 Token konnte nicht geholt werden.")
#         return

#     access_token = token_resp.json()["access_token"]

#     # Jetzt Admin-API aufrufen
#     headers = {"Authorization": f"Bearer {access_token}"}
#     admin_api_url = f"http://localhost:8080/admin/realms/{realm}/users"
#     response = requests.get(admin_api_url, headers=headers)

#     if response.status_code == 403 or response.status_code == 401:
#         print(f"[{realm}] ✅ Keine Privilege Escalation möglich")
#     else:
#         print(f"[{realm}] ❌ Privilege Escalation möglich – Zugriff mit User-Token!")


# def test_token_manipulation():
#     realm, client_secret, client_id, user_passwords = choose_realm()
#     user = random.choice(user_passwords)
#     user_username = user["username"]
#     user_password = user["password"]

#     login_url = get_login_url(realm, client_id)
#     driver.get(login_url)
#     wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user_username)
#     driver.find_element(By.ID, "password").send_keys(user_password)
#     driver.find_element(By.ID, "kc-login").click()

#     token = get_token(client_secret, client_id, realm)
#     manipulated_token = token[:-10] + "INVALIDTOK"

#     headers = {"Authorization": f"Bearer {manipulated_token}"}
#     admin_api_url = f"{base_url_local}/admin/realms/{realm}/users"
#     response = requests.get(admin_api_url, headers=headers)

#     if response.status_code == 401:
#         print(f"[{realm}] Token Manipulation Test: ✅ Token erkannt als ungültig")
#     else:
#         print(f"[{realm}] Token Manipulation Test: ❌ Token akzeptiert (Fehler!)")

# def test_dos():
#     realm, client_secret, client_id, user_passwords = choose_realm()
#     user = random.choice(user_passwords)
#     user_username = user["username"]
#     user_password = user["password"]

#     login_url = get_login_url(realm, client_id)
#     driver.get(login_url)
#     wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user_username)
#     driver.find_element(By.ID, "password").send_keys(user_password)
#     driver.find_element(By.ID, "kc-login").click()

#     # 50-mal hintereinander die Login-Seite laden (einfaches DoS)
#     for i in range(50):
#         driver.get(login_url)
#         print(f"[{realm}] DoS Load {i+1}/50 complete")

#     print(f"[{realm}] DoS Test abgeschlossen. Bitte Logs prüfen, ob Instabilität aufgetreten ist.")


def test_brute_force():
    realm, client_secret, client_id, _ = choose_realm()
    username = "admin"  # fester Benutzername
    password_list = [
        "admin123", "123456", "password", "letmein", "qwerty", "admin1", 
        "test123", "welcome", "root", "pass1234", "superadmin"
    ]  # Beispielhafte Passwortliste

    login_url = get_login_url(realm, client_id)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    for attempt, password in enumerate(password_list, 1):
        driver.get(login_url)

        # Eingabefelder ausfüllen
        wait.until(EC.presence_of_element_located((By.ID, "username"))).clear()
        driver.find_element(By.ID, "username").send_keys(username)

        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(password)

        driver.find_element(By.ID, "kc-login").click()

        print(f"[{realm}] Versuch {attempt}: {username} / {password}")

        # Optional: Erfolg prüfen (z. B. Weiterleitung oder Fehlermeldung)
        try:
            error_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-error")))
            print(f"⛔ Fehlgeschlagen mit Passwort: {password}")
        except:
            print(f"✅ Login möglicherweise erfolgreich mit Passwort: {password}")
            break  # Stoppen, wenn kein Fehler gefunden wurde

    driver.quit()
    print(f"[{realm}] Brute-Force-Test abgeschlossen.")



# Hauptprogramm: 10 Durchläufe
for i in range(8):
    print(f"--- Testlauf {i+1}/10 ---")
    #test_privilege_escalation()
    # test_token_manipulation()
    # test_dos()
    test_brute_force()

driver.quit()
