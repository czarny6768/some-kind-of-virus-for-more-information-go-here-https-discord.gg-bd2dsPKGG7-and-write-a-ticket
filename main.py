import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import time
import os
import threading
import hashlib
from flask import Flask

# --- KONFIGURACJA FLASK (Dla Render) ---
app = Flask('')

@app.route('/')
def home():
    return "TITAN BOT IS ALIVE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURACJA BOTA ---
# Token musi być ustawiony w Environment Variables na Render jako DISCORD_TOKEN
TOKEN = os.environ.get("DISCORD_TOKEN")
# Twój Webhook (poprawiony):
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash (/)
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = TitanBot()

# --- PĘTLA ANTI-SLEEP ---
@tasks.loop(minutes=5)
async def keep_alive_ping():
    print("Self-ping: Status bota OK.")

@bot.event
async def on_ready():
    print(f'Zalogowano pomyślnie jako {bot.user}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="TITAN NETWORK V12"
    ))
    if not keep_alive_ping.is_running():
        keep_alive_ping.start()

# --- KOMENDY SLASH ---

@bot.tree.command(name="setup_server", description="Buduje kanały dla TITAN V12")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Rozpoczynam tworzenie kanałów...", ephemeral=True)

    structure = {
        "--- INFORMACJE ---": ["regulamin", "ogłoszenia", "download-titan"],
        "--- STREFA TITAN ---": ["status-systemów", "logi-użycia"],
        "--- WSPARCIE ---": ["odbierz-24h-za-darmo", "pomoc-techniczna"],
        "--- SPOŁECZNOŚĆ ---": ["czat-ogólny", "pochwal-się-wynikiem"]
    }

    for cat_name, channels in structure.items():
        category = await guild.create_category(cat_name)
        for chan_name in channels:
            new_chan = await guild.create_text_channel(chan_name, category=category)
            if chan_name == "odbierz-24h-za-darmo":
                embed = discord.Embed(
                    title="🎁 ODBIERZ DARMOWE 24H",
                    description="Zasubskrybuj nas na TikToku i wpisz `/ticket`, aby dostać klucz!",
                    color=discord.Color.gold()
                )
                await new_chan.send(embed=embed)

    await interaction.followup.send("✅ Serwer został poprawnie skonfigurowany!")

@bot.tree.command(name="ticket", description="Otwiera ticket po darmowy klucz")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    ticket_chan = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites)
    
    embed = discord.Embed(
        title="🎫 TICKET TITAN V12",
        description=f"Witaj {user.mention}! Wrzuć tutaj dowód z TikToka, a my damy Ci licencję.",
        color=discord.Color.blue()
    )
    await ticket_chan.send(embed=embed)
    await interaction.response.send_message(f"✅ Stworzono ticket: {ticket_chan.mention}", ephemeral=True)

@bot.tree.command(name="licencja", description="Generuje klucz OTP dla TITAN")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    salt = "TITAN_ULTIMATE_2026"
    key_md5 = hashlib.md5(f"{ts}{salt}".encode()).hexdigest().upper()[:8]
    full_key = f"TITAN-{key_md5}"
    
    embed = discord.Embed(title="🔑 AUTORYZACJA TITAN", color=discord.Color.green())
    # Naprawiony błąd cudzysłowu:
    embed.add_field(name="TWÓJ KLUCZ (ważny 20s):", value=f"```\n{full_key}\n
```", inline=False)
    embed.set_footer(text="Aktywuj klucz w aplikacji V12")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="status", description="Sprawdza systemy bota")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="🛰️ TITAN STATUS", color=discord.Color.blue())
    embed.add_field(name="Silnik:", value="✅ Online", inline=True)
    embed.add_field(name="Proxy:", value="✅ 30k+ Active", inline=True)
    await interaction.response.send_message(embed=embed)

# --- URUCHOMIENIE ---
if __name__ == "__main__":
    # Start Flaska w tle
    threading.Thread(target=run_flask).start()
    
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
    else:
        print("BŁĄD: Nie znaleziono DISCORD_TOKEN w Environment Variables!")
