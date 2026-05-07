import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request
import threading
import uuid
import os

# --- KONFIGURACJA FLASK (API) ---
app = Flask(__name__)

# Lista aktywnych kluczy (TITAN-ADMIN-123 zostaje na zawsze dla Ciebie)
valid_keys = ["TITAN-ADMIN-123"]

@app.route('/')
def home():
    return "Serwer TITAN jest ONLINE"

@app.route('/auth')
def auth():
    key = request.args.get('key')
    if key in valid_keys:
        # Usuwamy klucz po użyciu, aby był jednorazowy (z wyjątkiem admina)
        if key != "TITAN-ADMIN-123":
            valid_keys.remove(key)
        return "SUCCESS"
    return "INVALID"

@app.route('/check_target')
def check():
    # Tutaj możesz dodać listę zablokowanych IP (np. rządowe)
    return "ALLOWED"

# --- KONFIGURACJA BOTA DISCORD ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash (/)
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = MyBot()

@bot.tree.command(name="licencja", description="Generuje jednorazowy klucz do programu TITAN")
async def licencja(interaction: discord.Interaction):
    # Generowanie losowego klucza (np. TITAN-A1B2C3D4)
    nowy_klucz = "TITAN-" + str(uuid.uuid4()).upper()[:8]
    valid_keys.append(nowy_klucz)
    
    embed = discord.Embed(title="💎 Nowa Licencja", color=0x00ff00)
    embed.add_field(name="Klucz", value=f"`{nowy_klucz}`", inline=False)
    embed.set_footer(text="Klucz jest jednorazowy i wygasnie po uzyciu w programie.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Uruchamianie Flask w tle na porcie 10000 (standard Rendera)
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Start serwera WWW
    threading.Thread(target=run_flask).start()
    # Start bota Discord (WPISZ SWÓJ TOKEN PONIŻEJ)
    bot.run("TWÓJ_TOKEN_BOTA_TUTAJ")
