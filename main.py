import discord
from discord import app_commands
import os
import random
import string
import time
from flask import Flask, jsonify
from threading import Thread

# --- BAZA KODÓW ---
active_codes = {} # { "KOD": czas_wygasniecia }

def create_code():
    return "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- SERWER WWW DLA SKRYPTU ---
app = Flask('')

@app.route('/verify/<user_code>')
def verify(user_code):
    now = time.time()
    if user_code in active_codes:
        if now < active_codes[user_code]:
            # Kod poprawny i świeży - usuwamy go (jednorazowy!)
            del active_codes[user_code]
            return jsonify({"auth": True})
    return jsonify({"auth": False}), 403

def run():
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class TitanAuth(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        
        @self.tree.command(name="generuj_kod", description="Generuje 10-minutowy token dostępu", guild=guild_id)
        async def generuj(interaction: discord.Interaction):
            # SPRAWDZANIE ROLI
            ROLE_ID = 1500513889064980661
            if not any(r.id == ROLE_ID for r in interaction.user.roles):
                return await interaction.response.send_message("❌ Nie masz rangi Customer!", ephemeral=True)

            code = create_code()
            active_codes[code] = time.time() + 600 # 10 minut
            
            emb = discord.Embed(title="🔑 TOKEN BEBLOBO TITAN", color=0x00ff00)
            emb.add_field(name="Kod", value=f"`{code}`")
            emb.set_footer(text="Ważny 10 minut | Jednorazowy")
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
