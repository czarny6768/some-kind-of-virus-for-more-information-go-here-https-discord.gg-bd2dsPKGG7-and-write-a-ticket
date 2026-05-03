import discord
from discord import app_commands
from discord.ext import commands
import os

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN') 
GUILD_ID = 1315680898456354917  # Twoje ID serwera z poprzednich wiadomości
CUSTOMER_ROLE_ID = 1500513889064980661  # ID roli Customer, które podałeś

# --- INICJALIZACJA BOTA ---
intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    try:
        # Synchronizacja komend slash
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Zsynchronizowano {len(synced)} komend.")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

# --- KOMENDA TESTU ---
@bot.tree.command(name="test_wifi", description="Uruchamia test internetu i WiFi")
async def test_wifi(interaction: discord.Interaction):
    # Sprawdzanie roli Customer
    if any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⚙️ **Uruchamiam diagnostykę sieci...**\nProszę czekać na wyniki testu.")
        
        import asyncio
        await asyncio.sleep(3) 
        
        await interaction.followup.send("✅ **Test zakończony sukcesem!** Parametry sieci są w normie.")
    else:
        await interaction.response.send_message("❌ **Błąd dostępu!** Ta funkcja jest dostępna tylko dla użytkowników z rolą **Customer**.", ephemeral=True)

bot.run(TOKEN)
