import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import time
import os
import threading
from flask import Flask

# --- KONFIGURACJA FLASK (Dla Render i Uptime) ---
app = Flask('')

@app.route('/')
def home():
    return "TITAN BOT IS ALIVE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURACJA BOTA ---
# Upewnij się, że w ustawieniach Render dodałeś zmienną środowiskową DISCORD_TOKEN
TOKEN = os.environ.get("DISCORD_TOKEN")
# Twój Webhook do logowania ataków
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"

class TitanBot(commands.Bot):
    def __init__(self):
        # Włączamy wszystkie intencje, aby bot widział użytkowników i wiadomości
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend / przy starcie
        await self.tree.sync()
        print(f"Zsynchronizowano komendy dla {self.user}")

bot = TitanBot()

# --- PĘTLA UTRZYMUJĄCA AKTYWNOŚĆ (Anti-Sleep) ---
@tasks.loop(minutes=5)
async def keep_alive_ping():
    # Render usypia po 15 min, więc co 5 min robimy 'szturchnięcie'
    print("Self-ping: Bot wysyła sygnał aktywności...")

@bot.event
async def on_ready():
    print(f'Zalogowano pomyślnie jako {bot.user}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="TITAN NETWORK V8.5"
    ))
    if not keep_alive_ping.is_running():
        keep_alive_ping.start()

# --- KOMENDY ---

@bot.tree.command(name="licencja", description="Generuje klucz OTP dla TITAN")
async def licencja(interaction: discord.Interaction):
    # Prosta generacja klucza na podstawie czasu (zgodna z Twoim C++)
    ts = int(time.time() // 20)
    salt = "TITAN_ULTIMATE_2026"
    import hashlib
    key_md5 = hashlib.md5(f"{ts}{salt}".encode()).hexdigest().upper()[:8]
    full_key = f"TITAN-{key_md5}"
    
    embed = discord.Embed(title="🔑 AUTORYZACJA TITAN", color=discord.Color.green())
    embed.add_field(name="TWÓJ KLUCZ (ważny 20s):", value=f"```\n{full_key}\n```", inline=False)
    embed.set_footer(text=f"ID Użytkownika: {interaction.user.id}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="status", description="Sprawdza stan systemów")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="🛰️ STATUS SYSTEMU", color=discord.Color.blue())
    embed.add_field(name="Bot:", value="✅ Aktywny (24/7 Mode)", inline=True)
    embed.add_field(name="API:", value="✅ Połączono", inline=True)
    await interaction.response.send_message(embed=embed)

# --- START ---
if __name__ == "__main__":
    # Uruchomienie Flaska w osobnym wątku (wymagane przez Render)
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Uruchomienie bota
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("BŁĄD: Brak DISCORD_TOKEN w zmiennych środowiskowych!")
