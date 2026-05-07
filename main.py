import os
from flask import Flask, request
import requests
import datetime

app = Flask(__name__)

# --- KONFIGURACJA ---
# Twój Webhook (sprawdź czy jest poprawny!)
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Baza kluczy: "Klucz": "HWID"
# Jeśli HWID to None, przypisze się przy pierwszym użyciu
database = {
    "TITAN-ADMIN-123": None,
    "SEBA-KLUCZ-2026": None
}

def send_discord(title, msg, color=16738740): # Różowy Hello Kitty
    payload = {
        "embeds": [{
            "title": title,
            "description": msg,
            "color": color,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except:
        pass

@app.route('/')
def home():
    return "TITAN SERVER STATUS: ONLINE"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')

    if not key or key not in database:
        return "INVALID_KEY"

    # Pierwsze logowanie
    if database[key] is None:
        database[key] = hwid
        send_discord("✅ AKTYWACJA", f"Klucz: `{key}`\nHWID: `{hwid}`")
        return "SUCCESS|ADMIN"

    # Sprawdzenie HWID
    if database[key] != hwid:
        send_discord("🚨 BLAD HWID", f"Klucz: `{key}`\nProba z HWID: `{hwid}`", color=16711680)
        return "HWID_MISMATCH"

    return "SUCCESS|ADMIN"

@app.route('/log_attack')
def log():
    key = request.args.get('key')
    target = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    
    send_discord("🔥 TEST SIECI", f"User: `{key}`\nCel: `{target}:{port}`\nCzas: `{time}s`", color=16753920)
    return "OK"

if __name__ == "__main__":
    # Render dynamicznie przypisuje port, musimy go pobrać
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
