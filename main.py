import os
import requests
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
# Wklej swój nowy Webhook poniżej
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Kolory dla Discorda (Hex -> Int)
COLOR_SUCCESS = 0x00FF7F  # Neonowa zieleń
COLOR_ATTACK  = 0xFF4500  # Krwista pomarańcza
COLOR_ERROR   = 0xFF0000  # Czerwień
COLOR_INFO    = 0x00BFFF  # Głęboki błękit

# Baza danych w pamięci (Klucz: {dane})
licenses = {
    "TITAN-ADMIN-123": {"hwid": None, "ranga": "OWNER", "expiry": "PERMANENT"},
    "SEBA-KLUCZ-2026": {"hwid": None, "ranga": "PREMIUM", "expiry": "2026-12-31"},
    "TEST-69-96": {"hwid": None, "ranga": "FREE", "expiry": "2026-06-01"}
}

# --- FUNKCJA WYSYŁANIA EMBEDÓW ---
def send_fancy_log(title, fields, color):
    payload = {
        "embeds": [{
            "title": f"🛡️ TITAN V2 | {title}",
            "color": color,
            "fields": fields,
            "footer": {"text": "Titan Multi-Tool System • v2.4", "icon_url": "https://i.imgur.com/8nS8v36.png"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print(f"Błąd Webhooka: {e}")

# --- TRASY SERWERA ---

@app.route('/')
def home():
    return "<h1>Titan Backend is Online</h1><p>Status: Ready to strike.</p>"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    ip = request.remote_addr

    if not key or key not in licenses:
        send_fancy_log("NIEAUTORYZOWANY DOSTĘP", [
            {"name": "⚠️ Próba Klucza", "value": f"`{key}`", "inline": True},
            {"name": "🌐 IP", "value": f"`{ip}`", "inline": True}
        ], COLOR_ERROR)
        return "INVALID_KEY"

    user_data = licenses[key]

    # Blokada HWID (Anti-Leak)
    if user_data["hwid"] is None:
        user_data["hwid"] = hwid
        send_fancy_log("NOWA AKTYWACJA", [
            {"name": "👤 User", "value": f"`{key}`", "inline": True},
            {"name": "🆔 HWID", "value": f"`{hwid}`", "inline": True},
            {"name": "⭐ Ranga", "value": user_data["ranga"], "inline": True}
        ], COLOR_SUCCESS)
        return f"SUCCESS|{user_data['ranga']}"

    if user_data["hwid"] != hwid:
        send_fancy_log("DETEKCJA MULTI-ACCOUNT", [
            {"name": "❌ Klucz", "value": key},
            {"name": "Oryginalny HWID", "value": user_data["hwid"]},
            {"name": "Złodziej HWID", "value": hwid}
        ], COLOR_ERROR)
        return "HWID_MISMATCH"

    return f"SUCCESS|{user_data['ranga']}"

@app.route('/log_attack')
def log_attack():
    key = request.args.get('key')
    host = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    method = request.args.get('method', 'UDP-TITAN')

    send_fancy_log("URUCHOMIONO TEST SIECI", [
        {"name": "👨‍💻 Operator", "value": f"`{key}`", "inline": True},
        {"name": "🎯 Cel", "value": f"`{host}:{port}`", "inline": True},
        {"name": "⏱️ Czas", "value": f"{time} sekund", "inline": True},
        {"name": "⚙️ Metoda", "value": method, "inline": False}
    ], COLOR_ATTACK)

    return "ATTACK_LOGGED"

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "active_keys": len(licenses),
        "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == "__main__":
    # Render używa zmiennej PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
