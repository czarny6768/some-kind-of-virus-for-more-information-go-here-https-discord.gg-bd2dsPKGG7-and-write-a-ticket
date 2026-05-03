import discord
from discord import app_commands
import os, random, string, time
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

# --- KONFIGURACJA SYSTEMU ---
active_tokens = {} 
user_usage = {}   

# TWOJE ZAKTUALIZOWANE ID RANG
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

def get_user_limit(member):
    current_limit = -1
    rank_name = None
    # Sprawdzamy wszystkie role użytkownika i wybieramy tę z najwyższym limitem
    for role_id, data in RANKS.items():
        if any(role.id == role_id for role in member.roles):
            if data["limit"] > current_limit:
                current_limit = data["limit"]
                rank_name = data["name"]
    return current_limit, rank_name

app = Flask('')

@app.route('/')
def home(): return "Beblobo Auth V3 - Active"

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        if str(data["user_id"]) == str(discord_id):
            # SPRAWDZANIE LIMITU CZASU (20 SEKUND)
            if now <= data["expiry"]:
                del active_tokens[user_code] # Jednorazowy użytek
                return jsonify({"auth": True})
            else:
                return jsonify({"auth": False, "reason": "Expired"}), 403
    return jsonify({"auth": False, "reason": "Invalid"}), 403

def run(): app.run(host='0.0.0.0', port=10000)

class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        
        @self.tree.command(name="licencja", description="Generuje unikalny kod (Ważny 20s)", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            user_id = interaction.user.id
            limit, r_name = get_user_limit(interaction.user)

            if limit == -1:
                return await interaction.response.send_message("❌ Nie posiadasz wymaganej rangi (Customer/Pro/Master)!", ephemeral=True)

            # RESET DZIENNY
            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["last_reset"] != today:
                user_usage[user_id] = {"count": 0, "last_reset": today}

            # SPRAWDZANIE CZY MOŻNA GENEROWAĆ
            if user_usage[user_id]["count"] >= limit:
                return await interaction.response.send_message(f"❌ Wykorzystałeś dzisiejszy limit ({limit}) dla rangi {r_name}!", ephemeral=True)

            # GENEROWANIE I NALICZANIE UŻYCIA (Próba znika w momencie generowania)
            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 20}
            user_usage[user_id]["count"] += 1 
            
            emb = discord.Embed(title=f"🔐 NOWA LICENCJA - {r_name.upper()}", color=0xFF0000)
            emb.add_field(name="TWÓJ KOD", value=f"**{code}**")
            emb.add_field(name="TWÓJ CZAS", value="⚡ **20 SEKUND** ⚡", inline=False)
            emb.add_field(name="LIMIT DZIENNY", value=f"Wykorzystano: {user_usage[user_id]['count']} / {limit if limit < 1000 else '∞'}")
            emb.set_footer(text="Kod jest jednorazowy. Pośpiesz się!")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)
        print("System licencyjny gotowy!")

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run).start()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
