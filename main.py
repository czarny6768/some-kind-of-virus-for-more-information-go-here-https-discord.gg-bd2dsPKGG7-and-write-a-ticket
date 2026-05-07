import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request
import threading
import uuid
import time
import requests

# --- KONFIGURACJA ---
TOKEN = "TWÓJ_TOKEN_BOTA" # <--- WKLEJ TUTAJ SWÓJ TOKEN
app = Flask(__name__)

ROLE_CONFIG = {
    1500513889064980661: {"name": "Zwykły Customer", "limit": 5},
    1500535408147173457: {"name": "Pro Customer", "limit": 10},
    1500535548438253771: {"name": "Customer Master", "limit": float('inf')}
}

valid_licenses = {"TITAN-ADMIN-123": None} 
user_usage = {}      
blacklisted_hosts = ["google.com", "gov.pl", "cia.gov"]

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot Titan online!")

bot = TitanBot()

# --- API DLA .EXE ---
@app.route('/')
def home(): return "TITAN API ONLINE"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    if key in valid_licenses: return "SUCCESS"
    return "INVALID"

@app.route('/check_target')
def check_target():
    target = request.args.get('host', '').lower()
    if any(blocked in target for blocked in blacklisted_hosts): return "BLOCKED"
    return "ALLOWED"

# --- KOMENDY DISCORD ---
@bot.tree.command(name="licencja", description="Generuje klucz licencji")
async def licencja(interaction: discord.Interaction):
    user = interaction.user
    limit = -1
    for role in user.roles:
        if role.id in ROLE_CONFIG:
            l = ROLE_CONFIG[role.id]["limit"]; limit = max(limit, l if l != float('inf') else 999999)

    if limit == -1:
        await interaction.response.send_message("❌ Brak roli klienta!", ephemeral=True)
        return

    now = time.time()
    uid = user.id
    user_usage[uid] = [t for t in user_usage.get(uid, []) if now - t < 86400]

    if limit != 999999 and len(user_usage[uid]) >= limit:
        await interaction.response.send_message(f"❌ Osiągnąłeś limit 24h!", ephemeral=True)
        return

    new_key = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_licenses[new_key] = None
    if limit != 999999: user_usage[uid].append(now)
    await interaction.response.send_message(f"✅ Klucz: `{new_key}`", ephemeral=True)

@bot.tree.command(name="bl", description="Blokuje strone/IP")
async def bl(interaction: discord.Interaction, host: str):
    blacklisted_hosts.append(host.lower())
    await interaction.response.send_message(f"🚫 Zablokowano cel: `{host}`")

# --- KEEP ALIVE ---
def keep_alive():
    while True:
        try:
            url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}.onrender.com/"
            requests.get(url)
        except: pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.run(TOKEN)
