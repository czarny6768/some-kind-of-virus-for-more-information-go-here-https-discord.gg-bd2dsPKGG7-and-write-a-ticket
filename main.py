import os
from flask import Flask, request
import requests
import datetime

app = Flask(__name__)

# --- KONFIGURACJA ---
# Upewnij się, że ten link jest poprawny!
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Baza: "Klucz": {"hwid": None, "status": "active"}
licenses = {
    "TITAN-ADMIN-123": {"hwid": None, "status": "active"},
    "SEBA-KLUCZ-2026": {"hwid": None, "status": "active"}
}

def notify_discord(title, fields, color=0xFF69B4): # Hello Kitty Pink
    data = {
        "embeds": [{
            "title": title,
            "fields": fields,
            "color": color,
            "footer": {"text": "Titan V2 - Power Control"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    except:
        pass

@app.route('/')
def index():
    return "Titan Hello Kitty Server is Running!"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    
    if key not in licenses:
        return "INVALID_KEY"
    
    user = licenses[key]
    
    if user["hwid"] is None:
        user["hwid"] = hwid
        notify_discord("✅ NOWA AKTYWACJA", [
            {"name": "Klucz", "value": key, "inline": True},
            {"name": "HWID", "value": hwid, "inline": True}
        ])
        return "SUCCESS|ADMIN"
    
    if user["hwid"] != hwid:
        notify_discord("🚨 PRÓBA ZŁODZIEJSTWA", [
            {"name": "Klucz", "value": key},
            {"name": "Próba HWID", "value": hwid}
        ], color=0xFF0000)
        return "HWID_MISMATCH"
        
    return "SUCCESS|ADMIN"

@app.route('/log_attack')
def log_attack():
    key = request.args.get('key')
    host = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    
    notify_discord("🔥 START TESTU", [
        {"name": "User", "value": key},
        {"name": "IP", "value": f"{host}:{port}"},
        {"name": "Czas", "value": f"{time}s"}
    ], color=0xFFA500)
    return "LOGGED"

if __name__ == "__main__":
    # Render wymaga bindowania do portu ze zmiennej środowiskowej
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
