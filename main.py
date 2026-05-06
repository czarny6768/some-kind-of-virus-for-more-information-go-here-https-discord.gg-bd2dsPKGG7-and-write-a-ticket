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

# TWOJE ID RANG - Upewnij się, że te ID zgadzają się z Twoim serwerem
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

# --- SERWER FLASK (Dla maszynki Titan) ---
app = Flask('')

@app.route('/')
def home():
    return "Beblobo Auth V3 - Online"

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
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # TWÓJ GUILD ID
        guild_id = discord.Object(id=1465510011445706892)
        
        # --- KOMENDA /NADAJ ---
        @self.tree.command(name="nadaj", description="Nadaje range na ilosc dni", guild=guild_id)
        @app_commands.checks.has_permissions(administrator=True)
        async def nadaj(interaction: discord.Interaction, uzytkownik: discord.Member, ranga: discord.Role, dni: int):
            expiry_date = datetime.now() + timedelta(days=dni)
            user_subscriptions[uzytkownik.id] = {"role_id": ranga.id, "expiry": expiry_date}
            try:
                await uzytkownik.add_roles(ranga)
                emb = discord.Embed(title="✅ NADAWANIU RANGI", color=0x2ECC71)
                emb.add_field(name="Osoba", value=uzytkownik.mention)
                emb.add_field(name="Ranga", value=ranga.name)
                emb.add_field(name="Dni", value=str(dni))
                emb.add_field(name="Wygasa", value=expiry_date.strftime("%Y-%m-%d"))
                await interaction.response.send_message(embed=emb)
            except:
                await interaction.response.send_message("❌ Blad uprawnien! Przesun bota wyzej w rolach.", ephemeral=True)

        # --- KOMENDA /INFO ---
        @self.tree.command(name="info", description="Informacje o Twojej randze", guild=guild_id)
        async def info(interaction: discord.Interaction):
            sub = user_subscriptions.get(interaction.user.id)
            emb = discord.Embed(title="ℹ️ TWOJE INFO", color=0x3498DB)
            if sub:
                remaining = sub["expiry"] - datetime.now()
                emb.add_field(name="Pozostalo dni", value=f"**{max(0, remaining.days)}**")
                emb.add_field(name="Data konca", value=f"`{sub['expiry'].strftime('%Y-%m-%d')}`")
            else:
                emb.add_field(name="Status", value="Brak aktywnej subskrypcji czasowej.")
            await interaction.response.send_message(embed=emb, ephemeral=True)

        # --- KOMENDA /LICENCJA ---
        @self.tree.command(name="licencja", description="Generuje kod 20s", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            limit = -1
            for r_id, data in RANKS.items():
                if any(role.id == r_id for role in interaction.user.roles):
                    limit = data["limit"]
            
            if limit == -1:
                return await interaction.response.send_message("❌ Nie masz rangi!", ephemeral=True)
            
            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": interaction.user.id, "expiry": time.time() + 20}
            
            emb = discord.Embed(title="🔐 KOD LICENCJI", color=0xFF0000)
            emb.add_field(name="KOD", value=f"**`{code}`**")
            emb.add_field(name="WAZNOSC", value="20 SEKUND")
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    # Pobieranie tokena z Environment Variables na Renderze
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        print("🚀 Serwer Beblobo startuje...")
        bot.run(TOKEN)
    else:
        print("❌ BLAD: Brak tokena w ustawieniach Rendera!")
