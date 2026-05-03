import discord
from discord import app_commands
import os
import random
import string
import time
import asyncio
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

# --- KONFIGURACJA SYSTEMU ---
active_tokens = {} 
user_usage = {}   

# TWOJE ID RANG
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

# --- SERWER FLASK (Dla Rendera i Skryptu) ---
app = Flask('')

@app.route('/')
def home():
    return "Beblobo Auth V3 - Monitoring Active"

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        if str(data["user_id"]) == str(discord_id):
            if now <= data["expiry"]:
                del active_tokens[user_code]
                return jsonify({"auth": True})
            else:
                return jsonify({"auth": False, "reason": "Expired"}), 403
    return jsonify({"auth": False, "reason": "Invalid"}), 403

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # Funkcja wysyłająca status co 15 minut na Twój kanał
    async def status_monitor_loop(self):
        await self.wait_until_ready()
        # TWOJE ID KANAŁU LOGÓW
        LOG_CHANNEL_ID = 1465516223096951026 
        channel = self.get_channel(LOG_CHANNEL_ID)

        while not self.is_closed():
            if channel:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                total_tokens = len(active_tokens)
                
                emb = discord.Embed(
                    title="📡 BEBLOBO MONITOR STATUS",
                    description="System autoryzacji działa poprawnie i czuwa nad licencjami.",
                    color=0x2ECC71 
                )
                emb.add_field(name="Godzina Raportu", value=f"`{now}`")
                emb.add_field(name="Aktywne kody (20s)", value=f"`{total_tokens}`")
                emb.set_footer(text="Automatyczny raport co 15 minut.")
                
                try:
                    await channel.send(embed=emb)
                except Exception as e:
                    print(f"Błąd wysyłania logów: {e}")
            
            await asyncio.sleep(900) 

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        
        # Uruchomienie monitoringu w tle
        self.loop.create_task(self.status_monitor_loop())
        
        @self.tree.command(name="licencja", description="Generuje kod licencji (Ważny 20s)", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            user_id = interaction.user.id
            
            limit = -1
            r_name = ""
            for role_id, data in RANKS.items():
                if any(role.id == role_id for role in interaction.user.roles):
                    if data["limit"] > limit:
                        limit = data["limit"]
                        r_name = data["name"]

            if limit == -1:
                return await interaction.response.send_message("❌ Nie posiadasz rangi (Customer/Pro/Master)!", ephemeral=True)

            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["last_reset"] != today:
                user_usage[user_id] = {"count": 0, "last_reset": today}

            if user_usage[user_id]["count"] >= limit:
                return await interaction.response.send_message(f"❌ Limit wykorzystany ({limit}) dla rangi {r_name}!", ephemeral=True)

            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 20}
            user_usage[user_id]["count"] += 1 
            
            emb = discord.Embed(title=f"🔐 LICENCJA WYGENEROWANA - {r_name.upper()}", color=0xFF0000)
            emb.add_field(name="KOD", value=f"**`{code}`**")
            emb.add_field(name="WAŻNOŚĆ", value="⌛ **20 SEKUND**", inline=False)
            emb.add_field(name="DZIŚ WYKORZYSTANO", value=f"{user_usage[user_id]['count']} / {limit if limit < 1000 else '∞'}")
            emb.set_footer(text="Wpisz kod szybko w programie Titan!")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("BŁĄD: Brak DISCORD_TOKEN na Renderze!")
