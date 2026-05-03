import discord
from discord import app_commands
import os
import random
import string
import time
from flask import Flask, jsonify
from threading import Thread

# --- LOGIKA KODÓW ---
active_codes = {} # Format: {"KOD": czas_wygasniecia}

def generate_random_code():
    return "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- SERWER WWW ---
app = Flask('')

@app.route('/verify/<code_input>')
def verify_code(code_input):
    current_time = time.time()
    # Sprawdzamy czy kod istnieje i czy nie minęło 10 minut (600s)
    if code_input in active_codes:
        expiry = active_codes[code_input]
        if current_time < expiry:
            # Kod poprawny - usuwamy go (jednorazowy!)
            del active_codes[code_input]
            return jsonify({"status": "success", "msg": "Access Granted"})
    
    return jsonify({"status": "error", "msg": "Invalid or expired code"}), 403

def run():
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=1465510011445706892)
        
        @self.tree.command(name="generuj_kod", description="Generuje 10-minutowy kod dostępu", guild=guild)
        async def generuj_kod(interaction: discord.Interaction):
            # ID TWOJEJ ROLI
            CUSTOMER_ROLE_ID = 1500513889064980661
            if not any(role.id == CUSTOMER_ROLE_ID for role in interaction.user.roles):
                return await interaction.response.send_message("❌ Nie masz roli Customer!", ephemeral=True)

            new_code = generate_random_code()
            active_codes[new_code] = time.time() + 600 # Ważny 10 min
            
            embed = discord.Embed(title="🔑 Twój kod dostępu", color=discord.Color.green())
            embed.add_field(name="Kod", value=f"`{new_code}`")
            embed.add_field(name="Ważność", value="10 minut")
            embed.set_footer(text="Kod jest jednorazowy.")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

        await self.tree.sync(guild=guild)

bot = MyBot()

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
