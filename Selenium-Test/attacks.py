import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# .env Variablen laden
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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

def test_privilege_escalation():
    driver.get(base_url_local + "/")
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user_username_local)
    driver.find_element(By.ID, "password").send_keys(user_password_local)
    driver.find_element(By.ID, "kc-login").click()
    
    # Versuch Admin-Seite aufzurufen
    driver.get(admin_url_local)
    # Prüfe ob Zugriff verweigert wird
    if "Access Denied" in driver.page_source or driver.current_url != admin_url_local:
        print("Privilege Escalation Test: Passed - Zugriff verweigert")
    else:
        print("Privilege Escalation Test: Failed - Zugriff möglich")

def get_token():
    data = {
        'client_id': client_id_local,
        'client_secret': client_secret_local,
        'grant_type': 'client_credentials'
    }
    resp = requests.post(token_url_local, data=data)
    resp.raise_for_status()
    token = resp.json()['access_token']
    return token

def test_token_manipulation():
    driver.get(base_url_local + "/")
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(admin_username_local)
    driver.find_element(By.ID, "password").send_keys(admin_password_local)
    driver.find_element(By.ID, "kc-login").click()

    token = get_token()
    manipulated_token = token[:-10] + "INVALIDTOK"

    headers = {"Authorization": f"Bearer {manipulated_token}"}
    response = requests.get(base_url_local + "/admin/realms/master/users", headers=headers)

    if response.status_code == 401:
        print("Token Manipulation Test: Passed - Token erkannt als ungültig")
    else:
        print("Token Manipulation Test: Failed - Token akzeptiert")

def test_dos():
    driver.get(base_url_local + "/")
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(admin_username_local)
    driver.find_element(By.ID, "password").send_keys(admin_password_local)
    driver.find_element(By.ID, "kc-login").click()

    # 50-mal hintereinander die User-Seite laden (einfaches DoS)
    for i in range(50):
        driver.get(admin_url_local)
        print(f"Load {i+1}/50 complete")

    print("DoS Test abgeschlossen. Bitte Logs prüfen, ob Instabilität aufgetreten ist.")

# Tests aufrufen
for i in range(10):
    test_privilege_escalation()
    test_token_manipulation()
    test_dos()

driver.quit()
