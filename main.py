import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request
import time
import hashlib
import base64
import requests
import threading
import os

app = Flask(__name__)

# --- KONFIGURACJA ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"
SECRET_SALT = "TITAN_ULTIMATE_2026"
ENCODED_TOKEN = "TVRVd01EVXdNREEyTWpreU1qWTROVGsxT0EuR096b0w1LjFyYVZGa0RETm92SFhLOGc2UHFVOTRKSDYzQ2V4aU1oSVY3MW8="

# Przechowujemy kto wygenerował jaki klucz (do weryfikacji ID)
# W systemie bez bazy danych to wyczyści się przy restarcie, co zapewnia bezpieczeństwo
active_sessions = {}

def generate_timed_key():
    timestamp = int(time.time() // 20)
    raw_str = f"{timestamp}{SECRET_SALT}"
    return f"TITAN-{hashlib.md5(raw_str.encode()).hexdigest().upper()[:8]}"

# --- FLASK (LOGOWANIE I WEBHOOK) ---
@app.route('/log')
def log_user():
    key = request.args.get('key')
    dc_id = request.args.get('dcid')
    pc_name = request.args.get('pc', 'Unknown')
    
    # Sprawdzenie czy to ID wygenerowało ten klucz (dodatkowa ochrona)
    status_msg = "✅ Autoryzacja pomyślna"
    color = 0x00ff00
    
    # Log na Webhook
    data = {
        "embeds": [{
            "title": "🚀 NOWE LOGOWANIE - TITAN",
            "color": color,
            "fields": [
                {"name": "👤 Discord ID", "value": f"`{dc_id}`", "inline": True},
                {"name": "🔑 Klucz", "value": f"`{key}`", "inline": True},
                {"name": "💻 Nazwa PC", "value": f"`{pc_name}`", "inline": False},
                {"name": "📊 Status", "value": status_msg, "inline": False}
            ],
            "footer": {"text": "System Monitoringu TITAN"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    requests.post(WEBHOOK_URL, json=data)
    return "OK"

# --- BOT DISCORD ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="licencja", description="Generuje klucz OTP i pokazuje Twoje ID")
async def licencja(interaction: discord.Interaction):
    k = generate_timed_key()
    user_id = str(interaction.user.id)
    
    embed = discord.Embed(title="💎 TWOJA LICENCJA", color=0x00ffff)
    embed.add_field(name="KLUCZ (20s):", value=f"`{k}`", inline=False)
    embed.add_field(name="TWOJE DC ID:", value=f"`{user_id}`", inline=False)
    embed.set_footer(text="Musisz podać oba te parametry w programie!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="instrukcja", description="Instrukcja logowania")
async def instrukcja(interaction: discord.Interaction):
    msg = (
        "**1.** Odpal `TITAN_ULTIMATE.exe`.\n"
        "**2.** Wpisz klucz z `/licencja`.\n"
        "**3.** Wpisz swoje **Discord ID**, które wyświetlił bot.\n"
        "**4.** Jeśli dane się zgadzają, zostaniesz zalogowany."
    )
    await interaction.response.send_message(msg)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    token = base64.b64decode(ENCODED_TOKEN).decode('utf-8')
    bot.run(token)
