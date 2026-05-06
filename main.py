import discord
from discord import app_commands
import os
import random
import string
import time
import asyncio
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime, timedelta

# --- KONFIGURACJA SYSTEMU ---
active_tokens = {} 
user_usage = {}   
user_subscriptions = {} # Przechowuje daty wygaśnięcia rang nadanych przez /nadaj

# TWOJE ID RANG (Zmień na właściwe ID ze swojego serwera)
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

# --- SERWER FLASK (API dla Twojej maszynki Titan) ---
app = Flask('')

@app.route('/')
def home():
    return "Beblobo Auth V3 - System Działa"

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
                return jsonify({"auth": False, "reason": "Kod wygasl"}), 403
    return jsonify({"auth": False, "reason": "Nieprawidlowy kod"}), 403

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def status_monitor_loop(self):
        await self.wait_until_ready()
        LOG_CHANNEL_ID = 1465516223096951026 
        channel = self.get_channel(LOG_CHANNEL_ID)
        while not self.is_closed():
            if channel:
                now = datetime.now().strftime("%H:%M:%S")
                emb = discord.Embed(title="📡 STATUS BEBLOBO", description="System działa poprawnie.", color=0x2ECC71)
                emb.add_field(name="Godzina", value=f"`{now}`")
                try: await channel.send(embed=emb)
                except: pass
            await asyncio.sleep(900) 

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        self.loop.create_task(self.status_monitor_loop())
        
        @self.tree.command(name="nadaj", description="Nadaje rangę na dni", guild=guild_id)
        @app_commands.checks.has_permissions(administrator=True)
        async def nadaj(interaction: discord.Interaction, uzytkownik: discord.Member, ranga: discord.Role, dni: int):
            expiry_date = datetime.now() + timedelta(days=dni)
            user_subscriptions[uzytkownik.id] = {"role_id": ranga.id, "expiry": expiry_date}
            try:
                await uzytkownik.add_roles(ranga)
                await interaction.response.send_message(f"✅ Nadano {ranga.name} dla {uzytkownik.mention} na {dni} dni.")
            except:
                await interaction.response.send_message("❌ Błąd uprawnień ról!")

        @self.tree.command(name="info", description="Sprawdza subskrypcję", guild=guild_id)
        async def info(interaction: discord.Interaction):
            sub = user_subscriptions.get(interaction.user.id)
            if sub:
                remaining = sub["expiry"] - datetime.now()
                await interaction.response.send_message(f"ℹ️ Pozostało dni: **{max(0, remaining.days)}**", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Brak aktywnej subskrypcji.", ephemeral=True)

        @self.tree.command(name="licencja", description="Kod 20s do maszynki", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            limit = -1
            for r_id, data in RANKS.items():
                if any(role.id == r_id for role in interaction.user.roles):
                    limit = data["limit"]
            if limit == -1: return await interaction.response.send_message("❌ Brak rangi!", ephemeral=True)
            
            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": interaction.user.id, "expiry": time.time() + 20}
            await interaction.response.send_message(f"🔐 Twój kod (20s): **`{code}`**", ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    # --- TO JEST NAJWAŻNIEJSZA LINIA ---
    # Pobiera token z zakładki Environment na Renderze
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        print("🚀 System Beblobo Auth V3 startuje...")
        bot.run(TOKEN)
    else:
        print("❌ BŁĄD: Nie ustawiono DISCORD_TOKEN na Renderze!")
