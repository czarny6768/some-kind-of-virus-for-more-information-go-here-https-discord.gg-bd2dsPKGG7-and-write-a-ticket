import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request
import threading
import uuid
import time
from datetime import datetime, timedelta

# --- KONFIGURACJA ---
TOKEN = "TWÓJ_TOKEN_BOTA"
app = Flask(__name__)

# ID RÓL I ICH LIMITY
ROLE_CONFIG = {
    1500513889064980661: {"name": "Zwykły Customer", "limit": 5},
    1500535408147173457: {"name": "Pro Customer", "limit": 10},
    1500535548438253771: {"name": "Customer Master", "limit": float('inf')} # Nieskończoność
}

# Baza danych w pamięci
valid_licenses = {"TITAN-ADMIN-123": None}
# Słownik do śledzenia użyć: {user_id: [lista_timestampów]}
user_usage = {}

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = TitanBot()

# --- HELPER: SPRAWDZANIE LIMITU ---
def check_limit(user):
    user_id = user.id
    current_time = time.time()
    
    # Znajdź najwyższą rolę użytkownika i przypisz limit
    user_limit = -1
    for role in user.roles:
        if role.id in ROLE_CONFIG:
            # Wybieramy najwyższy dostępny limit z posiadanych ról
            new_limit = ROLE_CONFIG[role.id]["limit"]
            if new_limit > user_limit:
                user_limit = new_limit

    if user_limit == -1:
        return False, "Brak uprawnień (nie masz odpowiedniej roli)."

    if user_limit == float('inf'):
        return True, user_limit

    # Usuń wpisy starsze niż 24h
    if user_id not in user_usage:
        user_usage[user_id] = []
    
    user_usage[user_id] = [t for t in user_usage[user_id] if current_time - t < 86400]

    if len(user_usage[user_id]) >= user_limit:
        # Oblicz za ile czasu zwolni się pierwszy slot
        wait_time = int((user_usage[user_id][0] + 86400) - current_time)
        hours = wait_time // 3600
        minutes = (wait_time % 3600) // 60
        return False, f"Osiągnąłeś limit 24h! Następny klucz dostępny za: {hours}h {minutes}m."

    return True, user_limit

# --- CZĘŚĆ: SERWER DLA .EXE (Flask) ---
@app.route('/auth')
def auth():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    if key not in valid_licenses: return "INVALID_KEY"
    if valid_licenses[key] is None:
        valid_licenses[key] = hwid
        return "SUCCESS|USER"
    return "SUCCESS|USER" if valid_licenses[key] == hwid else "HWID_MISMATCH"

# --- CZĘŚĆ: BOT DISCORD ---
@bot.tree.command(name="licencja", description="Generuje klucz z uwzględnieniem Twojego limitu")
async def licencja(interaction: discord.Interaction):
    can_gen, result = check_limit(interaction.user)

    if not can_gen:
        await interaction.response.send_message(f"❌ {result}", ephemeral=True)
        return

    # Generowanie
    new_key = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_licenses[new_key] = None
    
    # Zapisz użycie (chyba że master)
    if result != float('inf'):
        user_usage[interaction.user.id].append(time.time())

    count = "∞" if result == float('inf') else f"{len(user_usage[interaction.user.id])}/{result}"

    embed = discord.Embed(title="✅ Licencja Wygenerowana", color=0x00FF7F)
    embed.add_field(name="Klucz", value=f"`{new_key}`", inline=False)
    embed.add_field(name="Użycie 24h", value=f"`{count}`", inline=True)
    embed.set_footer(text="Klucz jest jednorazowy i przypisuje się do HWID.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)
