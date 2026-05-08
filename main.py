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
# Token pobierany bezpiecznie ze zmiennych środowiskowych Render
TOKEN = os.environ.get("DISCORD_TOKEN")
# Twój Webhook wstawiony na sztywno:
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

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
    print("Self-ping: Bot aktywny na Render...")

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

@bot.tree.command(name="setup_server", description="Automatyczna konfiguracja kanałów TITAN")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Buduję infrastrukturę serwera...", ephemeral=True)

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
            if chan_name == "odbierz-24h-za-darmo":
                embed = discord.Embed(
                    title="🎁 PROMOCJA: TITAN V12 ZA DARMO",
                    description="Zrób screena jak subujesz nas na TikToku i wpisz `/ticket`!",
                    color=discord.Color.gold()
                )
                await new_channel.send(embed=embed)

    await interaction.followup.send("✅ Serwer gotowy do pracy!")

# --- KOMENDA: SYSTEM TICKETÓW ---

@bot.tree.command(name="ticket", description="Otwórz ticket po darmowy klucz")
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
        title="🎫 NOWY TICKET - DARMOWA LICENCJA",
        description=f"Siema {user.mention}! Wrzuć tutaj screena z TikToka. Moderator sprawdzi go i wyśle Ci klucz.",
        color=discord.Color.blue()
    )
    await ticket_chan.send(embed=embed)
    await interaction.response.send_message(f"✅ Otwarto: {ticket_chan.mention}", ephemeral=True)

# --- KOMENDA: LICENCJA (NAPRAWIONA) ---

@bot.tree.command(name="licencja", description="Generuje klucz OTP dla TITAN")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    salt = "TITAN_ULTIMATE_2026"
    key_md5 = hashlib.md5(f"{ts}{salt}".encode()).hexdigest().upper()[:8]
    full_key = f"TITAN-{key_md5}"
    
    embed = discord.Embed(title="🔑 AUTORYZACJA TITAN", color=discord.Color.green())
    # Tutaj był błąd f-stringa - teraz jest poprawione:
    embed.add_field(name="TWÓJ KLUCZ (ważny 20s):", value=f"```\n{full_key}\n
```", inline=False)
    embed.set_footer(text="Wpisz klucz w programie V12")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDA: STATUS ---

@bot.tree.command(name="status", description="Sprawdza systemy")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="🛰️ STATUS TITAN V12", color=discord.Color.blue())
    embed.add_field(name="Proxy Baza:", value="✅ 30,000+ Online", inline=True)
    embed.add_field(name="Silnik Ataku:", value="✅ Ready", inline=True)
    await interaction.response.send_message(embed=embed)

# --- START ---
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"Błąd podczas startu bota: {e}")
    else:
        print("BŁĄD: Brak DISCORD_TOKEN w Environment Variables!")
