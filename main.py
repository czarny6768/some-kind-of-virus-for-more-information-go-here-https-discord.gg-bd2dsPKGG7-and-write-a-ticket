from flask import Flask, request
import requests
import os
import datetime

app = Flask(__name__)

# --- KONFIGURACJA ---
# Wklej tutaj swój link do Webhooka Discord
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

# Baza kluczy (Klucz : HWID)
# Na początku HWID jest None - przypisze się przy pierwszym zalogowaniu
licenses = {
    "TITAN-ADMIN-123": {"hwid": None, "ranga": "ADMIN", "banned": False},
    "SEBA-KLUCZ-2024": {"hwid": None, "ranga": "USER", "banned": False}
}

def send_to_discord(title, fields, color=3447003):
    payload = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": fields,
            "footer": {"text": "Titan V2 System"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass

@app.route('/')
def home():
    return "Titan Server Online - Hello Kitty Edition"

# --- SYSTEM AUTORYZACJI ---
@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    
    if not key or key not in licenses:
        return "INVALID_KEY", 401
    
    user = licenses[key]
    
    if user["banned"]:
        return "BANNED", 403
    
    # Pierwsze logowanie - przypisanie HWID
    if user["hwid"] is None:
        user["hwid"] = hwid
        send_to_discord("🆕 AKTYWACJA", [
            {"name": "Klucz", "value": key, "inline": True},
            {"name": "HWID", "value": hwid, "inline": True}
        ], color=65280) # Zielony
        return f"SUCCESS|{user['ranga']}"
    
    # Sprawdzanie czy HWID się zgadza
    if user["hwid"] != hwid:
        send_to_discord("🚨 PRÓBA WŁAMANIA", [
            {"name": "Klucz", "value": key},
            {"name": "Oryginalny HWID", "value": user["hwid"]},
            {"name": "Obecny HWID", "value": hwid}
        ], color=16711680) # Czerwony
        return "HWID_MISMATCH", 403
        
    return f"SUCCESS|{user['ranga']}"

# --- LOGOWANIE ATAKU ---
@app.route('/log_attack')
def log_attack():
    key = request.args.get('key')
    target = request.args.get('host')
    port = request.args.get('port')
    time = request.args.get('time')
    
    send_to_discord("🔥 TEST SIECI (UDP)", [
        {"name": "Operator", "value": key, "inline": True},
        {"name": "Cel", "value": f"{target}:{port}", "inline": True},
        {"name": "Czas", "value": f"{time}s", "inline": True}
    ], color=16753920) # Pomarańczowy
    
    return "OK"

# --- KOMENDY ADMINA (PRZEZ PRZEGLĄDARKĘ) ---
@app.route('/admin')
def admin():
    cmd = request.args.get('cmd')
    key = request.args.get('key')
    
    if key not in licenses:
        return "KEY_NOT_FOUND"
        
    if cmd == "resethwid":
        licenses[key]["hwid"] = None
        return f"SUCCESS: HWID dla {key} został zresetowany."
        
    if cmd == "ban":
        licenses[key]["banned"] = True
        return f"SUCCESS: Klucz {key} został zablokowany."
        
    return "UNKNOWN_COMMAND"

if __name__ == "__main__":
    # Render używa portu zdefiniowanego w zmiennej środowiskowej
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
