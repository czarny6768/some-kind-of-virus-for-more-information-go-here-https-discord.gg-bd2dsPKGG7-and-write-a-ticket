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
# ID RANG
ROLES_CONFIG = {
    1500535548438253771: {"name": "master", "limit": 999},
    1500535408147173457: {"name": "pro", "limit": 5},
    1500513889064980661: {"name": "customer", "limit": 2}
}

# Baza w pamięci RAM
db = {"keys": {}, "usage": {}}

# --- SERWER API (TO MUSI BYĆ W KODZIE!) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "TITAN AUTH IS ONLINE"

@app.route('/get_keys')
def get_keys():
    return jsonify(db["keys"])

# TA FUNKCJA JEST KLUCZOWA DLA JEDNORAZOWYCH KLUCZY
@app.route('/use_key/<key_to_delete>')
def use_key(key_to_delete):
    if key_to_delete in db["keys"]:
        del db["keys"][key_to_delete] # USUNIĘCIE KLUCZA Z BAZY
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 404

def run_api():
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
    print(f'✅ BOT I API GOTOWE')

@bot.tree.command(name="licencja", description="Generuje klucz")
async def licencja(interaction: discord.Interaction):
    user = interaction.user
    role_info = None
    for r_id, cfg in ROLES_CONFIG.items():
        if discord.utils.get(user.roles, id=r_id):
            role_info = cfg
            break
            
    if not role_info:
        return await interaction.response.send_message("❌ Brak rangi!", ephemeral=True)

    # Limit dzienny
    today = datetime.now().strftime("%Y-%m-%d")
    u_id = str(user.id)
    if u_id not in db["usage"] or db["usage"][u_id]["date"] != today:
        db["usage"][u_id] = {"date": today, "count": 0}

    if db["usage"][u_id]["count"] >= role_info["limit"]:
        return await interaction.response.send_message("❌ Limit wykorzystany!", ephemeral=True)

    # Generowanie
    key = f"{role_info['name']}-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    db["keys"][key] = role_info["name"]
    db["usage"][u_id]["count"] += 1

    await interaction.response.send_message(f"🔑 Twój klucz jednorazowy: `{key}`", ephemeral=True)

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    bot.run(TOKEN)
