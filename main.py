import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request
import threading
import uuid
import time

# --- KONFIGURACJA ---
TOKEN = "TWÓJ_TOKEN_BOTA"  # <--- WKLEJ TUTAJ SWÓJ TOKEN
app = Flask(__name__)

# ID RÓL I LIMITY
ROLE_CONFIG = {
    1500513889064980661: {"name": "Zwykły Customer", "limit": 5},
    1500535408147173457: {"name": "Pro Customer", "limit": 10},
    1500535548438253771: {"name": "Customer Master", "limit": float('inf')}
}

valid_licenses = {"TITAN-ADMIN-123": None}
user_usage = {}
blacklisted_hosts = ["google.com", "gov.pl"]

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot zalogowany!")

bot = TitanBot()

# --- TRASY SERWERA ---
@app.route('/')
def home(): return "TITAN AUTH SERVER ONLINE"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    if key in valid_licenses: return "SUCCESS"
    return "INVALID_KEY"

@app.route('/check_target')
def check_target():
    host = request.args.get('host', '').lower()
    if any(blocked in host for blocked in blacklisted_hosts): return "BLOCKED"
    return "ALLOWED"

# --- KOMENDA /LICENCJA ---
@bot.tree.command(name="licencja", description="Generuje klucz")
async def licencja(interaction: discord.Interaction):
    # Sprawdzenie roli
    has_role = any(role.id in ROLE_CONFIG for role in interaction.user.roles)
    if not has_role:
        await interaction.response.send_message("❌ Brak uprawnień!", ephemeral=True)
        return

    new_key = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_licenses[new_key] = None
    await interaction.response.send_message(f"✅ Twój klucz: `{new_key}`", ephemeral=True)

# --- URUCHAMIANIE ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ BŁĄD BOTA: {e}")
