import discord
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- MINIMALNY SERWER WWW ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online"
def run(): app.run(host='0.0.0.0', port=10000)

# --- BOT ---
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # To wysyła komendy na Twój serwer
        guild = discord.Object(id=1465510011445706892)
        self.tree.copy_from_slash_command(test_wifi)
        await self.tree.sync(guild=guild)
        print("Komendy zsynchronizowane!")

bot = MyBot()

@app_commands.command(name="test_wifi", description="Test")
async def test_wifi(interaction: discord.Interaction):
    await interaction.response.send_message("Bot działa i słucha!")

if __name__ == "__main__":
    Thread(target=run).start() # Start Flaska
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("BRAK TOKENA W USTWIENIACH RENDER!")
