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
user_subscriptions = {} 

# TWOJE ID RANG I LIMITY
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

app = Flask('')

@app.route('/')
def home():
    return "Beblobo Auth V3 - Limity Aktywne"

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        if str(data["user_id"]) == str(discord_id):
            if now <= data["expiry"]:
                del active_tokens[user_code]
                return jsonify({"auth": True})
    return jsonify({"auth": False}), 403

def run_flask():
    app.run(host='0.0.0.0', port=10000)

class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        
        # --- KOMENDA /NADAJ ---
        @self.tree.command(name="nadaj", description="Nadaje range na dni", guild=guild_id)
        @app_commands.checks.has_permissions(administrator=True)
        async def nadaj(interaction: discord.Interaction, uzytkownik: discord.Member, ranga: discord.Role, dni: int):
            expiry = datetime.now() + timedelta(days=dni)
            user_subscriptions[uzytkownik.id] = {"role_id": ranga.id, "expiry": expiry}
            try:
                await uzytkownik.add_roles(ranga)
                await interaction.response.send_message(f"✅ Nadano {ranga.name} dla {uzytkownik.mention} na {dni} dni.")
            except:
                await interaction.response.send_message("❌ Blad uprawnien roli bota!")

        # --- KOMENDA /LICENCJA (Z LIMITAMI) ---
        @self.tree.command(name="licencja", description="Generuje kod 20s (z limitami rang)", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            user_id = interaction.user.id
            
            # Sprawdzanie najwyższego dostępnego limitu dla użytkownika
            user_limit = -1
            r_name = ""
            for r_id, data in RANKS.items():
                if any(role.id == r_id for role in interaction.user.roles):
                    if data["limit"] > user_limit:
                        user_limit = data["limit"]
                        r_name = data["name"]

            if user_limit == -1:
                return await interaction.response.send_message("❌ Brak rangi! Nie mozesz generowac kodow.", ephemeral=True)

            # Resetowanie limitu dziennego
            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["date"] != today:
                user_usage[user_id] = {"count": 0, "date": today}

            # Sprawdzanie czy nie przekroczono limitu
            if user_usage[user_id]["count"] >= user_limit:
                return await interaction.response.send_message(f"❌ Wykorzystales dzienny limit ({user_limit}) dla rangi {r_name}!", ephemeral=True)

            # Generowanie kodu
            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 20}
            
            # Zwiekszenie licznika uzyc
            user_usage[user_id]["count"] += 1
            
            pozostalo = user_limit - user_usage[user_id]["count"]
            if user_limit > 1000: pozostalo = "∞"

            emb = discord.Embed(title="🔐 KOD WYGENEROWANY", color=0xFF0000)
            emb.add_field(name="KOD", value=f"**`{code}`**")
            emb.add_field(name="POZOSTAŁO DZIŚ", value=f"**{pozostalo}**")
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        print("🚀 System Beblobo z limitami wystartowal!")
        bot.run(TOKEN)
