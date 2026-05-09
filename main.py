import discord
from discord import app_commands
from discord.ext import commands
import hashlib
import time
import os
from flask import Flask
from threading import Thread

# --- KONFIGURACJA FLASK (Dla Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Titan V12 Bot is running!"

def run_flask():
    # Render używa portu 10000 lub wartości ze zmiennej PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- KONFIGURACJA BOT DISCORD ---
TOKEN = os.getenv('DISCORD_TOKEN')
SALT = "TITAN_ULTIMATE_2026" 

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla: {self.user}")

bot = TitanBot()

def get_md5_short(data):
    return hashlib.md5(data.encode()).hexdigest().upper()[:8]

# --- KOMENDY SLASH ---

@bot.tree.command(name="gen", description="Generuje tymczasowy klucz licencyjny")
async def gen(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    key_hash = get_md5_short(str(ts) + SALT)
    current_key = f"TITAN-{key_hash}"
    
    embed = discord.Embed(title="🛡️ TITAN V12 - AUTH", color=0x00ff00)
    embed.add_field(name="KLUCZ:", value=f"`{current_key}`", inline=False)
    embed.set_footer(text="Klucz wygasa za 20 sekund!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket", description="Otwiera nowy kanał wsparcia")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    channel_name = f"ticket-{user.name.lower()}"

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
    
    embed = discord.Embed(title="🎫 TICKET OTWARTY", description=f"Witaj {user.mention}!", color=0x3498db)
    embed.add_field(name="INFO", value="Opisz swój problem lub wpisz /gen, aby dostać klucz.")
    
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Stworzono: {channel.mention}", ephemeral=True)

@bot.tree.command(name="close", description="Usuwa kanał ticketu")
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("Usuwanie kanału...")
        time.sleep(2)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ To nie jest kanał ticketu!", ephemeral=True)

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    if TOKEN:
        keep_alive() # Uruchamia serwer WWW w tle dla Render
        bot.run(TOKEN)
    else:
        print("BŁĄD: Nie ustawiono zmiennej DISCORD_TOKEN!")
