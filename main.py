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

# --- SERWER FLASK (API dla Twojego skryptu Titan) ---
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
    # Render używa domyślnie portu 10000
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # Automatyczny raport statusu co 15 minut
    async def status_monitor_loop(self):
        await self.wait_until_ready()
        LOG_CHANNEL_ID = 1465516223096951026 
        channel = self.get_channel(LOG_CHANNEL_ID)

        while not self.is_closed():
            if channel:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                total_tokens = len(active_tokens)
                emb = discord.Embed(
                    title="📡 BEBLOBO MONITOR STATUS",
                    description="System autoryzacji działa poprawnie.",
                    color=0x2ECC71 
                )
                emb.add_field(name="Godzina", value=f"`{now}`")
                emb.add_field(name="Aktywne kody", value=f"`{total_tokens}`")
                try:
                    await channel.send(embed=emb)
                except:
                    pass
            await asyncio.sleep(900) 

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        self.loop.create_task(self.status_monitor_loop())
        
        # --- KOMENDA /NADAJ ---
        @self.tree.command(name="nadaj", description="Nadaje rangę użytkownikowi na dni", guild=guild_id)
        @app_commands.checks.has_permissions(administrator=True)
        async def nadaj(interaction: discord.Interaction, uzytkownik: discord.Member, ranga: discord.Role, dni: int):
            expiry_date = datetime.now() + timedelta(days=dni)
            user_subscriptions[uzytkownik.id] = {"role_id": ranga.id, "expiry": expiry_date}
            
            try:
                await uzytkownik.add_roles(ranga)
                emb = discord.Embed(title="✅ NADANO RANGĘ", color=0x2ECC71)
                emb.add_field(name="Osoba", value=uzytkownik.mention)
                emb.add_field(name="Ranga", value=ranga.name)
                emb.add_field(name="Wygasa", value=f"{expiry_date.strftime('%Y-%m-%d')}")
                await interaction.response.send_message(embed=emb)
            except:
                await interaction.response.send_message("❌ Brak uprawnień bota do nadawania ról!", ephemeral=True)

        # --- KOMENDA /INFO ---
        @self.tree.command(name="info", description="Sprawdza status Twojej licencji", guild=guild_id)
        async def info(interaction: discord.Interaction):
            user_id = interaction.user.id
            sub = user_subscriptions.get(user_id)
            
            emb = discord.Embed(title="ℹ️ STATUS LICENCJI", color=0x3498DB)
            if sub:
                remaining = sub["expiry"] - datetime.now()
                emb.add_field(name="Pozostało dni", value=f"**{max(0, remaining.days)}**", inline=False)
                emb.add_field(name="Wygasa", value=f"`{sub['expiry'].strftime('%Y-%m-%d')}`", inline=False)
            else:
                emb.add_field(name="Subskrypcja", value="Nie masz aktywnej subskrypcji czasowej.")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        # --- KOMENDA /LICENCJA ---
        @self.tree.command(name="licencja", description="Generuje kod do programu Titan (20s)", guild=guild_id)
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
                return await interaction.response.send_message("❌ Nie masz odpowiedniej roli (Customer+)! ", ephemeral=True)

            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["last_reset"] != today:
                user_usage[user_id] = {"count": 0, "last_reset": today}

            if user_usage[user_id]["count"] >= limit:
                return await interaction.response.send_message(f"❌ Wykorzystałeś limit dla rangi {r_name}!", ephemeral=True)

            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 20}
            user_usage[user_id]["count"] += 1 
            
            emb = discord.Embed(title="🔐 KOD WYGENEROWANY", color=0xFF0000)
            emb.add_field(name="TWÓJ KOD", value=f"**`{code}`**")
            emb.add_field(name="WAŻNY PRZEZ", value="⌛ 20 SEKUND")
            emb.set_footer(text="Użyj komendy /info aby sprawdzić czas trwania rangi.")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    # Start serwera Flask (do weryfikacji przez skrypt)
    Thread(target=run_flask).start()
    
    # POBIERANIE TOKENA ZE ZMIENNYCH ŚRODOWISKOWYCH (Bezpieczne!)
    # W panelu Render.com dodaj zmienną o nazwie DISCORD_TOKEN
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        print("🚀 Serwer Beblobo startuje...")
        bot.run(TOKEN)
    else:
        print("❌ BŁĄD: Brak zmiennej DISCORD_TOKEN! Dodaj ją w ustawieniach hostingu.")
