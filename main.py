import discord
from discord import app_commands
from discord.ext import commands
import os, threading, hashlib, time
from flask import Flask, jsonify, request

# --- API DLA C++ ---
app = Flask('')
blacklisted_hwids = ["BAN-ID-123"] # Lista zbanowanych urządzeń

@app.route('/check_auth', methods=['GET'])
def check_auth():
    hwid = request.args.get('hwid')
    if hwid and hwid.upper() in blacklisted_hwids:
        return jsonify({"status": "banned"}), 403
    return jsonify({"status": "ok"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# --- BOT DISCORD ---
TOKEN = os.environ.get("DISCORD_TOKEN")
SECRET_SALT = "TITAN_V12_SECURE_SALT_2026" # Musi być identyczny w C++

class TitanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        await self.tree.sync()

bot = TitanBot()

@bot.tree.command(name="licencja", description="Generuje 20-sekundowy klucz jednorazowy")
async def licencja(interaction: discord.Interaction):
    # Sprawdzenie rangi Customer
    if not any(role.name == "Customer" for role in interaction.user.roles):
        await interaction.response.send_message("❌ Brak rangi Customer!", ephemeral=True)
        return

    # Generowanie klucza czasowego (ważny ok. 20-30s)
    # Dzielimy czas przez 20, aby klucz zmieniał się co 20 sekund
    time_step = int(time.time() // 20)
    raw_key = f"{time_step}{SECRET_SALT}"
    final_key = hashlib.md5(raw_key.encode()).hexdigest().upper()[:8]

    embed = discord.Embed(title="🔑 KLUCZ JEDNORAZOWY", color=0x00ff00)
    embed.add_field(name="Klucz:", value=f"`TITAN-{final_key}`")
    embed.set_footer(text="Ważny przez 20 sekund! Pośpiesz się z logowaniem.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="bl_add", description="Banuje HWID")
@app_commands.checks.has_permissions(administrator=True)
async def bl_add(interaction: discord.Interaction, hwid: str):
    blacklisted_hwids.append(hwid.upper())
    await interaction.response.send_message(f"🚫 HWID `{hwid}` zbanowany.", ephemeral=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
