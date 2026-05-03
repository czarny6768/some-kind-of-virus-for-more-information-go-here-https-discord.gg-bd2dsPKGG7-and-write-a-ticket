import discord
from discord import app_commands
import os
import random
import string
import time
from flask import Flask, jsonify
from threading import Thread

# --- BAZA TOKENÓW ---
# Format: { "KOD": {"user_id": 123, "expiry": 456} }
active_tokens = {}

def create_token():
    return "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

app = Flask('')

@app.route('/')
def home(): return "Beblobo Secure Auth Online"

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        # Sprawdzamy czy ID się zgadza i czy kod nie wygasł
        if str(data["user_id"]) == str(discord_id) and now < data["expiry"]:
            del active_tokens[user_code] # KOD JEST JEDNORAZOWY
            return jsonify({"auth": True})
    
    return jsonify({"auth": False, "reason": "Invalid, expired or wrong user"}), 403

def run():
    app.run(host='0.0.0.0', port=10000)

class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        
        @self.tree.command(name="licencja", description="Generuje przypisany do konta kod 10-minutowy", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            ROLE_ID = 1500513889064980661
            if not any(r.id == ROLE_ID for r in interaction.user.roles):
                return await interaction.response.send_message("❌ Brak rangi Customer!", ephemeral=True)

            code = create_token()
            active_tokens[code] = {
                "user_id": interaction.user.id,
                "expiry": time.time() + 600
            }
            
            emb = discord.Embed(title="🔐 PRYWATNA LICENCJA", color=0x7289DA)
            emb.add_field(name="Twój Kod", value=f"**{code}**")
            emb.add_field(name="Twoje ID", value=f"`{interaction.user.id}`", inline=False)
            emb.set_footer(text="Kod zadziała TYLKO z Twoim ID Discord i wygaśnie po 10 min.")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run).start()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
