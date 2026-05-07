import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import uuid
import time

# --- KONFIGURACJA ---
TOKEN = "TWÓJ_TOKEN_BOTA"  # <--- WKLEJ TUTAJ SWÓJ TOKEN
app = Flask(__name__)

# ID RÓL I LIMITY (Poprawione na Twoje ID)
ROLE_CONFIG = {
    1500513889064980661: {"name": "Zwykły Customer", "limit": 5},
    1500535408147173457: {"name": "Pro Customer", "limit": 10},
    1500535548438253771: {"name": "Customer Master", "limit": float('inf')}
}

# BAZA DANYCH W PAMIĘCI
valid_licenses = {"TITAN-ADMIN-123": None} # Klucze : HWID
user_usage = {}      # user_id : [lista czasów użycia]
blacklisted_hwids = []
blacklisted_hosts = ["google.com", "gov.pl"] # Przykładowe blokady

# --- BOT SETUP ---
class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
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

# --- TRASY SERWERA DLA .EXE ---
@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    
    if hwid in blacklisted_hwids: return "BLACKLISTED_HWID"
    if key not in valid_licenses: return "INVALID_KEY"
    
    if valid_licenses[key] is None:
        valid_licenses[key] = hwid
        return "SUCCESS|REGISTERED"
    
    return "SUCCESS|LOGGED" if valid_licenses[key] == hwid else "HWID_MISMATCH"

@app.route('/check_target')
def check_target():
    target = request.args.get('host')
    if target in blacklisted_hosts:
        return "BLOCKED"
    return "ALLOWED"

# --- KOMENDY DISCORD ---

@bot.tree.command(name="licencja", description="Generuje klucz licencji")
async def licencja(interaction: discord.Interaction):
    limit = get_user_limit(interaction.user)
    
    if limit == -1:
        await interaction.response.send_message("❌ Nie masz uprawnień! Musisz mieć odpowiednią rolę klienta.", ephemeral=True)
        return

    # Logika limitu 24h
    if limit != float('inf'):
        now = time.time()
        uid = interaction.user.id
        user_usage[uid] = [t for t in user_usage.get(uid, []) if now - t < 86400]
        if len(user_usage[uid]) >= limit:
            await interaction.response.send_message(f"❌ Osiągnąłeś limit {limit} kluczy na 24h!", ephemeral=True)
            return
        user_usage[uid].append(now)

    new_key = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_licenses[new_key] = None
    
    emb = discord.Embed(title="🛡️ TITAN AUTH", color=0x00FF7F)
    emb.add_field(name="TWÓJ KLUCZ", value=f"`{new_key}`", inline=False)
    emb.set_footer(text="Klucz jest jednorazowy i przypisany do Twojego HWID.")
    await interaction.response.send_message(embed=emb, ephemeral=True)

@bot.tree.command(name="bl", description="Blokuje HWID lub Stronę")
@app_commands.choices(typ=[
    app_commands.Choice(name="HWID (Komputer)", value="hwid"),
    app_commands.Choice(name="HOST (Strona/IP)", value="host")
])
async def bl(interaction: discord.Interaction, typ: str, wartosc: str):
    # Tutaj możesz dodać sprawdzanie, czy tylko ADMIN może użyć /bl
    if typ == "hwid":
        blacklisted_hwids.append(wartosc)
        msg = f"🚫 Zablokowano HWID: `{wartosc}`"
    else:
        blacklisted_hosts.append(wartosc.lower())
        msg = f"🚫 Dodano stronę `{wartosc}` do listy zakazanych celów."
    
    await interaction.response.send_message(msg)

# --- URUCHAMIANIE ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
