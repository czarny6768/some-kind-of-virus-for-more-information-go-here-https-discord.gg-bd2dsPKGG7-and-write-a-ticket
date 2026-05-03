import discord
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- 1. SERWER WWW (Utrzymanie bota przy życiu na Renderze) ---
app = Flask('')

@app.route('/')
def home():
    return "Serwer BebloboAuth jest aktywny!"

def run():
    # Używamy portu 10000, aby uniknąć błędów port scan timeout
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. KONFIGURACJA I FILTRY ---
# Używamy ID serwera dostarczonego przez Ciebie: 1465510011445706892
MY_GUILD = discord.Object(id=1465510011445706892)
CUSTOMER_ROLE_ID = 1500513889064980661

class BebloboBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # Wymagane przez Privileged Intents (image_fe979b.png)
        super().__init__(intents=intents)
        # Tworzymy drzewo komend (baza danych komend bota)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Synchronizacja bazy komend z serwerem Discord
        self.tree.copy_from_slash_command(test_wifi)
        self.tree.copy_from_slash_command(pomoc)
        await self.tree.sync(guild=MY_GUILD)
        print(f"Baza danych komend zsynchronizowana dla serwera {MY_GUILD.id}")

bot = BebloboBot()

# --- 3. BAZA KOMEND (Tutaj dopisuj nowe komendy) ---

@app_commands.command(name="test_wifi", description="Uruchamia diagnostykę sieci dla klientów")
async def test_wifi(interaction: discord.Interaction):
    """Komenda sprawdzająca uprawnienia roli Customer"""
    has_role = any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles)
    
    if has_role:
        await interaction.response.send_message("✅ **Diagnostyka WiFi uruchomiona.** Sprawdzanie stabilności łącza...")
    else:
        await interaction.response.send_message("❌ Błąd: Ta komenda wymaga roli **Customer**.", ephemeral=True)

@app_commands.command(name="pomoc", description="Wyświetla listę dostępnych funkcji bota")
async def pomoc(interaction: discord.Interaction):
    """Prosta komenda informacyjna dostępna dla każdego"""
    embed = discord.Embed(title="Panel Pomocy BebloboAuth", color=discord.Color.blue())
    embed.add_field(name="/test_wifi", value="Diagnostyka sieci (tylko dla Customer)", inline=False)
    embed.add_field(name="/status", value="Sprawdza czy bot jest online", inline=False)
    await interaction.response.send_message(embed=embed)

# --- 4. URUCHOMIENIE ---
@bot.event
async def on_ready():
    print(f'Zalogowano pomyślnie jako: {bot.user}')

if __name__ == "__main__":
    keep_alive() # Uruchamia Flask w tle (rozwiązuje problem z image_fe8fbb.png)
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("CRITICAL ERROR: Nie znaleziono DISCORD_TOKEN!")
