import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- PROSTY SERWER WWW DLA RENDER ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- KONFIGURACJA BOTA ---
TOKEN = os.getenv('DISCORD_TOKEN') 
GUILD_ID = 1315680898456354917  
CUSTOMER_ROLE_ID = 1500513889064980661 

intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Zsynchronizowano {len(synced)} komend.")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

@bot.tree.command(name="test_wifi", description="Uruchamia test internetu i WiFi")
async def test_wifi(interaction: discord.Interaction):
    if any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⚙️ **Uruchamiam diagnostykę sieci...**")
        # Tu logika testu...
    else:
        await interaction.response.send_message("❌ Brak dostępu!", ephemeral=True)

# URUCHOMIENIE
keep_alive() # To "oszuka" Rendera
bot.run(TOKEN)
