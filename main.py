import os
import discord
from discord import app_commands
import random
import string
import json
import threading
from flask import Flask, jsonify
from datetime import datetime

# --- KONFIGURACJA ---
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_IDS = [1315680898456354917, 1152563201590956072]

# Rangi i ich limity (0 = brak limitu dla mastera)
ROLES_CONFIG = {
    1500535548438253771: {"name": "master", "limit": 999999},
    1500535408147173457: {"name": "pro", "limit": 10},
    1500513889064980661: {"name": "customer", "limit": 5}
}

# Baza danych w pamięci (Render i tak czyści pliki, więc to najlepsze rozwiązanie)
db = {"keys": {}, "usage": {}}

# --- SERWER API DLA TITANA (Naprawia błąd Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "TITAN API IS ONLINE"

@app.route('/get_keys')
def get_keys():
    return jsonify(db["keys"])

def run_api():
    # Render wymaga bindowania portu
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT DISCORD ---
class TitanBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'✅ BOT ONLINE: {bot.user}')

@bot.tree.command(name="licencja", description="Generuje klucz licencyjny")
async def licencja(interaction: discord.Interaction):
    user = interaction.user
    
    # Sprawdzanie rangi
    role_info = None
    for r_id, cfg in ROLES_CONFIG.items():
        if discord.utils.get(user.roles, id=r_id):
            role_info = cfg
            break
            
    if not role_info:
        await interaction.response.send_message("❌ Brak wymaganej rangi!", ephemeral=True)
        return

    # Limity dzienne
    today = datetime.now().strftime("%Y-%m-%d")
    u_id = str(user.id)
    if u_id not in db["usage"] or db["usage"][u_id]["date"] != today:
        db["usage"][u_id] = {"date": today, "count": 0}

    if db["usage"][u_id]["count"] >= role_info["limit"]:
        await interaction.response.send_message("❌ Limit wykorzystany!", ephemeral=True)
        return

    # Generowanie klucza
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    key = f"{role_info['name']}-{suffix}"
    
    db["keys"][key] = role_info["name"]
    db["usage"][u_id]["count"] += 1

    await interaction.response.send_message(f"🔑 Twój klucz: `{key}`\nRanga: **{role_info['name'].upper()}**", ephemeral=True)

if __name__ == "__main__":
    # Start API w tle
    threading.Thread(target=run_api, daemon=True).start()
    bot.run(TOKEN)
