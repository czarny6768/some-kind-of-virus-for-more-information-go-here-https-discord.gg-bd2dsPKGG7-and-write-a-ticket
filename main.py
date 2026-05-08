import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import time
import os
import threading
import hashlib
from flask import Flask

# --- KONFIGURACJA FLASK ---
app = Flask('')

@app.route('/')
def home():
    return "TITAN BOT IS ALIVE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURACJA BOTA ---
TOKEN = os.environ.get("DISCORD_TOKEN")
# Pamiętaj, aby nie udostępniać publicznie Webhooka!
WEBHOOK_URL = "TWÓJ_WEBHOOK_URL"

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = TitanBot()

@tasks.loop(minutes=5)
async def keep_alive_ping():
    print("Self-ping: Bot aktywny...")

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="TITAN NETWORK V12"
    ))
    if not keep_alive_ping.is_running():
        keep_alive_ping.start()

# --- KOMENDA: BUDOWA SERWERA ---

@bot.tree.command(name="setup_server", description="Buduje strukturę kanałów TITAN V12")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Rozpoczynam budowę serwera...", ephemeral=True)

    # Kategorie i kanały
    categories = {
        "--- INFORMACJE ---": ["regulamin", "ogłoszenia", "download-titan"],
        "--- STREFA TITAN ---": ["status-systemów", "logi-użycia"],
        "--- WSPARCIE ---": ["odbierz-24h-za-darmo", "pomoc-techniczna"],
        "--- SPOŁECZNOŚĆ ---": ["czat-ogólny", "pochwal-się-wynikiem"]
    }

    for cat_name, channels in categories.items():
        category = await guild.create_category(cat_name)
        for chan_name in channels:
            new_channel = await guild.create_text_channel(chan_name, category=category)
            
            # Dodaj wiadomość powitalną na kanale ticketów
            if chan_name == "odbierz-24h-za-darmo":
                embed = discord.Embed(
                    title="🎁 PROMOCJA: TITAN V12 ZA DARMO",
                    description="Zrób screena jak subujesz nas na TikToku i wpisz `/ticket`!",
                    color=discord.Color.gold()
                )
                await new_channel.send(embed=embed)

    await interaction.followup.send("✅ Serwer gotowy!")

# --- KOMENDA: SYSTEM TICKETÓW ---

@bot.tree.command(name="ticket", description="Otwiera ticket w sprawie darmowej licencji")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    
    # Tworzenie prywatnego kanału
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    ticket_chan = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites)
    
    embed = discord.Embed(
        title="🎫 NOWY TICKET",
        description=f"Witaj {user.mention}! Wrzuć tutaj dowód (screen) z TikToka, aby otrzymać klucz.",
        color=discord.Color.blue()
    )
    await ticket_chan.send(embed=embed)
    await interaction.response.send_message(f"✅ Stworzono ticket: {ticket_chan.mention}", ephemeral=True)

# --- TWOJE STARE KOMENDY (LICENCJA I STATUS) ---

@bot.tree.command(name="licencja", description="Generuje klucz OTP dla TITAN")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    salt = "TITAN_ULTIMATE_2026"
    key_md5 = hashlib.md5(f"{ts}{salt}".encode()).hexdigest().upper()[:8]
    full_key = f"TITAN-{key_md5}"
    
    embed = discord.Embed(title="🔑 AUTORYZACJA TITAN", color=discord.Color.green())
    embed.add_field(name="TWÓJ KLUCZ (ważny 20s):", value=f"```\n{full_key}\n
```", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="status", description="Sprawdza stan systemów")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="🛰️ STATUS SYSTEMU", color=discord.Color.blue())
    embed.add_field(name="V12 Engine:", value="✅ Online", inline=True)
    embed.add_field(name="Proxy Nodes:", value="✅ 30,000+ Active", inline=True)
    await interaction.response.send_message(embed=embed)

# --- START ---
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("BŁĄD: Brak DISCORD_TOKEN!")
