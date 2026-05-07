import discord
from discord.ext import commands
import time, hashlib, base64, requests, threading, os
from flask import Flask, request

app = Flask(__name__)

# --- KONFIGURACJA ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1501964599313039382/G4LaDablfU8cajOZsXHZX7j3JXWUMFQxG-DNPeSOg8nkkPNhOAvscq26ac7SZ9SFmayo"
SECRET_SALT = "TITAN_ULTIMATE_2026"
ENCODED_TOKEN = "TVRVd01EVXdNREEyTWpreU1qWTROVGsxT0EuR096b0w1LjFyYVZGa0RETm92SFhLOGc2UHFVOTRKSDYzQ2V4aU1oSVY3MW8="

def get_otp():
    ts = int(time.time() // 20)
    return hashlib.md5(f"{ts}{SECRET_SALT}".encode()).hexdigest().upper()[:8]

@app.route('/attack')
def handle_attack():
    key = request.args.get('key')
    host = request.args.get('host')
    port = request.args.get('port')
    duration = request.args.get('time')
    method = request.args.get('method')
    dcid = request.args.get('dcid')
    pc = request.args.get('pc')

    if key != f"TITAN-{get_otp()}":
        return "UNAUTHORIZED", 403

    # Wysyłanie logu na Webhook
    log_data = {
        "embeds": [{
            "title": "⚡ TITAN COMMAND EXECUTED",
            "color": 0xFF0000,
            "fields": [
                {"name": "👤 OPERATOR", "value": f"ID: `{dcid}`\nPC: `{pc}`", "inline": False},
                {"name": "🎯 TARGET", "value": f"`{host}:{port}`", "inline": True},
                {"name": "🛠️ METHOD", "value": f"`{method}`", "inline": True},
                {"name": "⏱️ TIME", "value": f"`{duration}s`", "inline": True}
            ],
            "footer": {"text": "TITAN NETWORK COMMANDER v7.0"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }]
    }
    requests.post(WEBHOOK_URL, json=log_data)
    return "SUCCESS"

# --- BOT DISCORD ---
class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self): await self.tree.sync()

bot = TitanBot()

@bot.tree.command(name="licencja", description="Generuje dynamiczny klucz i podaje Twoje ID")
async def licencja(interaction: discord.Interaction):
    k = f"TITAN-{get_otp()}"
    embed = discord.Embed(title="🔑 AUTORYZACJA TITAN", color=0x00FF00)
    embed.add_field(name="TWÓJ KLUCZ (20s):", value=f"```\n{k}\n```", inline=False)
    embed.add_field(name="TWOJE DC ID:", value=f"`{interaction.user.id}`", inline=False)
    embed.set_footer(text="Klucz wygaśnie za chwilę. Pośpiesz się!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

def run_api():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_api).start()
    bot.run(base64.b64decode(ENCODED_TOKEN).decode())
