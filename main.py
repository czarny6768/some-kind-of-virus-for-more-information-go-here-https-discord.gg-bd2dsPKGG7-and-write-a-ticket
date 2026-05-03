import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- 1. SERWER WWW (Żeby Render nie wyłączał bota - naprawia błąd z image_ff0837.png) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot BebloboAuth działa!"

def run():
    # Render wymaga portu 10000 lub zmiennej PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KONFIGURACJA BOTA ---
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = 1465510011445706892  # Twoje ID serwera z czatu
CUSTOMER_ROLE_ID = 1500513889064980661 # ID Twojej roli

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # To jest kluczowe: rejestrujemy komendy dla Twojego serwera
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_from_slash_command(test_wifi) # Kopiujemy komendę do drzewa
        await self.tree.sync(guild=guild)
        print(f"Zsynchronizowano komendy dla serwera: {GUILD_ID}")

bot = MyBot()

# --- 3. DEFINICJA KOMENDY SLASH ---
@app_commands.command(name="test_wifi", description="Uruchamia diagnostykę sieci i WiFi")
async def test_wifi(interaction: discord.Interaction):
    # Sprawdzamy czy użytkownik ma rolę Customer
    user_has_role = any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles)
    
    if user_has_role:
        await interaction.response.send_message("⚙️ **Uruchamiam diagnostykę sieci...** Proszę czekać na wynik testu.")
    else:
        await interaction.response.send_message("❌ Nie masz uprawnień! Ta komenda jest tylko dla osób z rolą Customer.", ephemeral=True)

# --- 4. URUCHOMIENIE ---
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name} (ID: {bot.user.id})')
    print('------')

if __name__ == "__main__":
    keep_alive() # Startujemy serwer Flask w tle
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("BŁĄD: Nie znaleziono DISCORD_TOKEN w zmiennych środowiskowych Render!")
