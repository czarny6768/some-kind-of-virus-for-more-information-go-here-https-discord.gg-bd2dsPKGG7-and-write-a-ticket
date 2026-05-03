import discord
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Serwer Flask dla Rendera (zapobiega usypianiu)
app = Flask('')
@app.route('/')
def home(): return "BebloboAuth is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run).start()

# Konfiguracja (Używamy Twoich ID)
GUILD_ID = 1465510011445706892 
CUSTOMER_ROLE_ID = 1500513889064980661

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Zaznaczyłeś to na image_fe979b.png
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # WYMUSZONA REJESTRACJA NA TWOIM SERWERZE
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_from_slash_command(test_wifi)
        self.tree.copy_from_slash_command(status)
        
        # To jest kluczowe: czyścimy i wgrywamy od nowa
        await self.tree.sync(guild=guild)
        print(f"BAZA KOMEND ZAŁADOWANA NA SERWER: {GUILD_ID}")

bot = MyBot()

@app_commands.command(name="test_wifi", description="Uruchamia test WiFi")
async def test_wifi(interaction: discord.Interaction):
    if any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⚙️ Diagnostyka w toku...")
    else:
        await interaction.response.send_message("❌ Brak roli Customer.", ephemeral=True)

@app_commands.command(name="status", description="Sprawdza stan bota")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Bot BebloboAuth działa poprawnie!")

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("BŁĄD: Brak TOKENA w Environment Variables!")
