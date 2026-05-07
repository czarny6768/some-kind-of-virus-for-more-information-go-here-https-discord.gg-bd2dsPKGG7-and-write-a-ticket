from flask import Flask, request, jsonify
import requests
import datetime
import os

app = Flask(__name__)

# --- KONFIGURACJA ---
# Tu wklej swój Webhook z Discorda
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Twoja lista kluczy (Klucz : Dane)
licenses = {
    "TITAN-ADMIN-123": {"hwid": None, "ranga": "ADMIN", "banned": False},
    "SEBA-TEST-999": {"hwid": None, "ranga": "USER", "banned": False}
}

def send_to_discord(title, fields, color=3447003):
    payload = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": fields,
            "footer": {"text": "Titan V2 Logging System"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except:
        pass

@app.route('/')
def home():
    return "Titan Server Online"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    
    if key not in licenses:
        return "INVALID_KEY", 401
    
    user = licenses[key]
    if user["banned"]: return "BANNED", 403
    
    if user["hwid"] is None:
        user["hwid"] = hwid
        send_to_discord("🆕 AKTYWACJA KLUCZA", [{"name": "Klucz", "value": key}, {"name": "HWID", "value": hwid}])
    elif user["hwid"] != hwid:
        return "HWID_MISMATCH", 403
        
    return f"SUCCESS|{user['ranga']}"

@app.route('/log_attack')
def log():
    key = request.args.get('key')
    target = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    
    send_to_discord("🔥 URUCHOMIONO TEST", [
        {"name": "Klucz", "value": key, "inline": True},
        {"name": "Cel", "value": f"{target}:{port}", "inline": True},
        {"name": "Czas", "value": f"{time}s", "inline": True}
    ], color=15105570)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
