from flask import Flask, request, jsonify
import requests
import datetime
import os

app = Flask(__name__)

# --- KONFIGURACJA ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Baza kluczy
licenses = {
    "TITAN-ADMIN-123": {"hwid": None, "ranga": "ADMIN", "banned": False},
    "SEBA-KLUCZ-2024": {"hwid": None, "ranga": "USER", "banned": False}
}

def send_to_discord(title, fields, color=3447003):
    payload = {
        "embeds": [{
            "title": title, "color": color, "fields": fields,
            "footer": {"text": "Titan System"}, "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except: pass

@app.route('/')
def home():
    return "Titan API is Online. Use /auth for client."

# --- KOMENDY ADMINA (używasz w przeglądarce) ---
# Przykład: /admin?cmd=resethwid&key=TITAN-ADMIN-123
@app.route('/admin')
def admin_cmds():
    cmd = request.args.get('cmd')
    key = request.args.get('key')
    
    if key not in licenses: return "KEY_NOT_FOUND", 404
    
    if cmd == "resethwid":
        licenses[key]["hwid"] = None
        return f"SUCCESS: HWID for {key} has been reset."
    
    if cmd == "ban":
        licenses[key]["banned"] = True
        return f"SUCCESS: {key} has been banned."

    return "INVALID_COMMAND", 400

# --- AUTORYZACJA KLIENTA ---
@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    if key not in licenses: return "INVALID_KEY", 401
    user = licenses[key]
    if user["banned"]: return "BANNED", 403
    
    if user["hwid"] is None:
        user["hwid"] = hwid
        send_to_discord("🆕 AKTYWACJA", [{"name": "Klucz", "value": key}, {"name": "HWID", "value": hwid}])
    elif user["hwid"] != hwid:
        return "HWID_MISMATCH", 403
    return f"SUCCESS|{user['ranga']}"

@app.route('/log_attack')
def log():
    key = request.args.get('key')
    target = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    send_to_discord("🔥 TEST SIECI", [
        {"name": "Operator", "value": key, "inline": True},
        {"name": "Cel", "value": f"{target}:{port}", "inline": True},
        {"name": "Czas", "value": f"{time}s", "inline": True}
    ], color=15105570)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
