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

# ID RÓL I LIMITY
ROLE_CONFIG = {
    1500513889064980661: {"name": "Zwykły Customer", "limit": 5},
    1500535408147173457: {"name": "Pro Customer", "limit": 10},
    1500535548438253771: {"name": "Customer Master", "limit": float('inf')}
}

# BAZA DANYCH W PAMIĘCI
valid_licenses = {"TITAN-ADMIN-123": None} # Klucz : HWID
user_usage = {}      # user_id : [lista czasów użycia]
blacklisted_hosts = ["google.com", "gov.pl", "cia.gov"]

# --- BOT SETUP ---
class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot Titan zalogowany jako {self.user}")

bot = TitanBot()

# --- FUNKCJE POMOCNICZE ---
def get_user_limit(user):
    max_limit = -1
    for role in user.roles:
        if role.id in ROLE_CONFIG:
            l = ROLE_CONFIG[role.id]["limit"]
            if l == float('inf'): return float('inf')
            if l > max_limit: max_limit = l
    return max_limit

# --- TRASY SERWERA DLA .EXE (FLASK) ---
@app.route('/')
def home():
    return "TITAN AUTH SERVER IS ONLINE"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    if key not in valid_licenses: return "INVALID_KEY"
    if valid_licenses[key] is None:
        valid_licenses[key] = hwid
        return "SUCCESS|REGISTERED"
    return "SUCCESS|LOGGED" if valid_licenses[key] == hwid else "HWID_MISMATCH"

@app.route('/check_target')
def check_target():
    target = request.args.get('host', '').lower()
    if any(blocked in target for blocked in blacklisted_hosts):
        return "BLOCKED"
    return "ALLOWED"

# --- KOMENDY DISCORD ---

@bot.tree.command(name="licencja", description="Generuje klucz licencji (limit 24h)")
async def licencja(interaction: discord.Interaction):
    limit = get_user_limit(interaction.user)
    
    if limit == -1:
        await interaction.response.send_message("❌ Nie masz uprawnień! Musisz posiadać rolę klienta.", ephemeral=True)
        return

    # Logika limitu 24h
    now = time.time()
    uid = interaction.user.id
    if uid not in user_usage: user_usage[uid] = []
    
    # Czyścimy stare użycia (>24h)
    user_usage[uid] = [t for t in user_usage[uid] if now - t < 86400]

    if limit != float('inf') and len(user_usage[uid]) >= limit:
        await interaction.response.send_message(f"❌ Osiągnąłeś limit {limit} kluczy na 24h!", ephemeral=True)
        return

    # Generowanie klucza
    new_key = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_licenses[new_key] = None
    if limit != float('inf'): user_usage[uid].append(now)

    embed = discord.Embed(title="🛡️ TITAN AUTH SYSTEM", color=0x00FF7F)
    embed.add_field(name="KLUCZ LICENCYJNY", value=f"`{new_key}`", inline=False)
    embed.add_field(name="POZOSTALO UZYC", value=f"`{ 'Nieskonczonosc' if limit == float('inf') else f'{limit - len(user_usage[uid])}/{limit}' }`", inline=True)
    embed.set_footer(text="Klucz jest jednorazowy i przypisuje się do Twojego HWID.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="bl", description="Blokuje stronę (Blacklista)")
async def bl(interaction: discord.Interaction, strona: str):
    # Możesz dodać sprawdzanie czy użytkownik to Ty (Admin)
    blacklisted_hosts.append(strona.lower())
    await interaction.response.send_message(f"🚫 Strona `{strona}` została zablokowana w systemie TITAN.")

# --- SYSTEM KEEP-ALIVE (Żeby Render nie usypiał bota) ---
def keep_alive():
    while True:
        try:
            # Pingowanie własnej strony co 10 minut
            if os.environ.get('RENDER_EXTERNAL_URL'):
                requests.get(os.environ.get('RENDER_EXTERNAL_URL'))
        except:
            pass
        time.sleep(600)

# --- URUCHAMIANIE ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Flask w tle
    threading.Thread(target=run_flask, daemon=True).start()
    # Ping w tle
    threading.Thread(target=keep_alive, daemon=True).start()
    # Bot główny
    bot.run(TOKEN)
