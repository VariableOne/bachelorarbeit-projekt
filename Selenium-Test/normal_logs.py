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

# Setup
options = Options()
options.add_argument("--headless")  # Headless-Modus für CI/CD
driver = webdriver.Chrome(options=options)

load_dotenv()

client_id_local = os.getenv("client_id_local")
client_secret_local = os.getenv("client_secret_local")
token_url_local = os.getenv("token_url_local")
event_url_local = os.getenv("event_url_local")

base_url_local = os.getenv("base_url_local")
admin_url_local = os.getenv("admin_url_local")

user_username_local = os.getenv("user_username_local")
user_password_local = os.getenv("user_password_local")

admin_username_local = os.getenv("admin_username_local")
admin_password_local = os.getenv("admin_password_local")

realm = os.getenv("realm_local")
client_two = os.getenv("client_two")

def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Nutzernamenliste
names = [
    'Anna', 'Bob', 'Carlos', 'Diana', 'Elena', 'Faisal', 'Gina', 'Hiroshi', 'Isabel',
    'Jamal', 'Klara', 'Luca', 'Maya', 'Nina', 'Omar', 'Priya', 'Quentin', 'Rina',
    'Sofia', 'Tom', 'Usha', 'Victor', 'Wei', 'Yara', 'Zane'
]
user_pool = names[:25]

# Funktionen
def simulate_login(username, password):
    login_url = f"{base_url_local}/realms/{realm}/protocol/openid-connect/auth?client_id={client_two}&response_type=code&scope=openid&redirect_uri={base_url_local}"
    driver.get(login_url)

    time.sleep(1)
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "kc-login").click()
    time.sleep(1)

def simulate_login_error():
    simulate_login("wronguser", "wrongpass")

def simulate_refresh_token():
    print(f"Simuliere Refresh Token gegen {token_url_local} ... (nur per API möglich)")

def simulate_admin_actions():
    driver.get(f"{base_url_local}/admin/")
    time.sleep(1)
    driver.find_element(By.ID, "username").send_keys(admin_username_local)
    driver.find_element(By.ID, "password").send_keys(admin_password_local)
    driver.find_element(By.ID, "kc-login").click()
    time.sleep(2)
    print("Simuliere Admin-Aktion wie Benutzer-Update, -Get oder -Delete...")

with open("user_passwords.json", "r") as f:
    user_passwords = json.load(f)


for i in range(1000):
    random_user = random.choice(user_passwords)
    username_now = random_user["username"]
    password_now = random_user["password"]

    simulate_login(username_now, password_now)

    if random.random() < 0.3:
        simulate_login_error()

    if random.random() < 0.2:
        simulate_refresh_token()

    if random.random() < 0.05:
        simulate_admin_actions()

driver.quit()
print("Test abgeschlossen.")
