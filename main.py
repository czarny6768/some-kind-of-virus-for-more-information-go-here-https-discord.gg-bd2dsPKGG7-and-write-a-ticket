import discord
from discord import app_commands
import os
import random
import string
import time
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime

# --- KONFIGURACJA ---
GUILD_ID = 1465510011445706892
ID_ROLI_OWNER = 1465514077366518033

# Mapowanie ID ról na limity w maszynce
RANKS_CONFIG = {
    1465514077366518033: {"name": "OWNER", "limit": 1500},
    1500535548438253771: {"name": "MASTER", "limit": 1500},
    1500535408147173457: {"name": "PRO", "limit": 400},
    1500513889064980661: {"name": "CUSTOMER", "limit": 150}
}

active_tokens = {} # Kody tymczasowe do maszynki
user_usage = {}   # Licznik dzienny

app = Flask('')

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    # Bypass dla Ownera
    if user_code.lower() == "beblobo":
        return jsonify({"auth": True, "info": "Bypass"}), 200

    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        if str(data["user_id"]) == str(discord_id) and now <= data["expiry"]:
            del active_tokens[user_code]
            return jsonify({"auth": True}), 200
            
    return jsonify({"auth": False}), 403

def run_flask():
    app.run(host='0.0.0.0', port=10000)

class TitanV2(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # KLUCZOWE: Pozwala czytać rangi z DC
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild_obj = discord.Object(id=GUILD_ID)

        @self.tree.command(name="licencja", description="Pobiera kod na podstawie Twoich rang na DC", guild=guild_obj)
        async def licencja(interaction: discord.Interaction):
            user = interaction.user
            user_id = user.id
            
            # SPRAWDZANIE RANG BEZPOŚREDNIO Z DISCORDA
            max_limit = -1
            ranga_name = "BRAK"
            
            for role in user.roles:
                if role.id in RANKS_CONFIG:
                    cfg = RANKS_CONFIG[role.id]
                    if cfg["limit"] > max_limit:
                        max_limit = cfg["limit"]
                        ranga_name = cfg["name"]

            # Jeśli użytkownik jest Adminem lub Ownerem
            if user.guild_permissions.administrator or any(r.id == ID_ROLI_OWNER for r in user.roles):
                max_limit = 1500
                ranga_name = "OWNER/ADMIN"

            if max_limit == -1:
                return await interaction.response.send_message("❌ Nie posiadasz żadnej roli uprawniającej do użycia TitanV2!", ephemeral=True)

            # Limit dzienny
            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["date"] != today:
                user_usage[user_id] = {"count": 0, "date": today}

            if ranga_name != "OWNER/ADMIN" and user_usage[user_id]["count"] >= max_limit:
                return await interaction.response.send_message(f"❌ Wykorzystałeś limit dla rangi {ranga_name}!", ephemeral=True)

            # Generowanie kodu
            code = "TITAN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 30}
            user_usage[user_id]["count"] += 1

            embed = discord.Embed(title="🔐 TITAN V2 - AUTORYZACJA", color=0x00ffff)
            embed.add_field(name="TWÓJ KOD", value=f"**`{code}`**", inline=False)
            embed.add_field(name="RANGA WYKRYTA", value=f"**{ranga_name}**", inline=True)
            embed.add_field(name="WAŻNOŚĆ", value="30 sekund", inline=True)
            embed.set_footer(text="Wpisz kod w maszynce, aby uzyskać dostęp.")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

        await self.tree.sync(guild=guild_obj)

bot = TitanV2()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
