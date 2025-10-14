import os
import base64
import requests
from datetime import datetime
from dotenv import dotenv_values

# ---------------------------------------------------------------------
# Admin Portal Login
# ---------------------------------------------------------------------

ADMIN_LOGIN_CACHE = {}

def adminlogin(env_path, format=None):
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f".env file not found at: {env_path}")
    
    creds = dotenv_values(env_path)
    if format == "ENCODED":
        username = base64.b64decode(creds.get("FERMA_USERNAME") or b"").decode()
        password = base64.b64decode(creds.get("FERMA_PASSWORD") or b"").decode()
    else:
        username = creds.get("FERMA_USERNAME")
        password = creds.get("FERMA_PASSWORD")

    if not username or not password:
        raise ValueError("Missing FERMA_USERNAME or FERMA_PASSWORD in env file")

    cache_key = (username, password)
    if cache_key in ADMIN_LOGIN_CACHE:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]: (Cache) Ferma Admin Portal Login successful")
        return ADMIN_LOGIN_CACHE[cache_key]

    try:
        resp = requests.post(
            "https://admin-portal.ferma.ai/users/login",
            json={"username": username, "password": password, "persist": 1},
            timeout=10
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Admin login failed: network error: {e}")

    if resp.status_code == 401:
        try:
            msg = resp.json().get("message") or resp.json().get("error")
        except ValueError:
            msg = resp.text or "Unauthorized"
        raise RuntimeError(f"Admin login failed (401 Unauthorized): {msg}")

    if resp.status_code != 200:
        raise RuntimeError(f"Admin login failed: HTTP {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError("Admin login failed: response not valid JSON")

    token = data.get("accessToken")
    if not token:
        msg = data.get("message") or data.get("error") or resp.text
        raise RuntimeError(f"Admin login failed: {msg}")

    headers = {"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"}
    ADMIN_LOGIN_CACHE[cache_key] = headers
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]: Ferma Admin Portal Login successful")
    return headers


# ---------------------------------------------------------------------
# Support Portal Login
# ---------------------------------------------------------------------

session = None

def supportlogin(env_path):
    global session
    
    login_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://support.ferma.ai/main/login"
    }
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f".env file not found at: {env_path}")
    
    creds = dotenv_values(env_path)
    session = requests.Session()
    session.get("https://support.ferma.ai/main/login")

    login_data = {
        "username": creds.get("FERMA_USERNAME"),
        "password": creds.get("FERMA_PASSWORD")
    }
    resp = session.post("https://support.ferma.ai/main/validate", data=login_data, headers=login_headers)
    
    if resp.status_code != 200:
        raise Exception(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]: Login failed - HTTP {resp.status_code}")

    # Case 1: Invalid credentials detected in response text
    if "Invalid credentials" in resp.text or "Error" in resp.text:
        raise Exception(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]: Login failed - Invalid credentials")

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]: Ferma Support Portal Login successful")
    return session