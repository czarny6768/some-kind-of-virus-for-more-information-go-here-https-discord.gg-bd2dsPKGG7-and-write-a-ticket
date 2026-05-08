import discord
from discord import app_commands
from discord.ext import commands
import time
import os
import threading
import hashlib
from flask import Flask, jsonify, request

# --- KONFIGURACJA FLASK (API DLA C++) ---
app = Flask('')

# Baza danych w pamięci (warto zapisać do pliku .txt lub json)
blacklisted_hwids = ["PRZYKLAD-HWID-123"] 
verified_users = {} # Format: {discord_id: "login_z_dc"}

@app.route('/check_hwid', methods=['GET'])
def check_hwid():
    # Twój program w C++ wysyła: GET /check_hwid?hwid=UNIKALNE_ID
    user_hwid = request.args.get('hwid')
    if not user_hwid:
        return jsonify({"status": "error", "message": "No HWID provided"}), 400
    
    if user_hwid.upper() in blacklisted_hwids:
        return jsonify({"status": "banned", "message": "Twoje urządzenie jest zablokowane!"}), 403
    return jsonify({"status": "ok", "message": "Dostęp przyznany"}), 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURACJA BOTA DISCORD ---
TOKEN = os.environ.get("DISCORD_TOKEN")

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = TitanBot()

# --- KOMENDA: PROFESJONALNY SETUP SERWERA ---

@bot.tree.command(name="setup_server_full", description="Buduje serwer TITAN od podstaw")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server_full(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Budowanie profesjonalnej struktury TITAN...", ephemeral=True)

    # 1. Rangi
    verified_role = discord.utils.get(guild.roles, name="Verified") or await guild.create_role(name="Verified", color=discord.Color.green())
    customer_role = discord.utils.get(guild.roles, name="Customer") or await guild.create_role(name="Customer", color=discord.Color.blue())

    # 2. Kanał Weryfikacji (Regulamin)
    overwrites_ver = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        verified_role: discord.PermissionOverwrite(read_messages=False)
    }
    ch_ver = await guild.create_text_channel("🛡️┃weryfikacja", overwrites=overwrites_ver)

    # Długi, profesjonalny regulamin
    rules = (
        "**TITAN NETWORK - TERMS OF SERVICE**\n\n"
        "1. Akceptując regulamin, potwierdzasz przypisanie swojego konta Discord do urządzenia (HWID).\n"
        "2. System Stresser służy wyłącznie do testów obciążeniowych własnej infrastruktury.\n"
        "3. Próby debugowania lub modyfikacji klienta C++ skutkują permanentnym banem HWID.\n"
        "4. Blacklista HWID jest nieodwołalna.\n\n"
        "**Aby przejść dalej, wpisz: `accept`**"
    )
    await ch_ver.send(embed=discord.Embed(title="📜 REGULAMIN SYSTEMU", description=rules, color=discord.Color.red()))

    # 3. Kategorie Streserów i Panelu
    over_v = {guild.default_role: discord.PermissionOverwrite(read_messages=False), verified_role: discord.PermissionOverwrite(read_messages=True)}
    
    cat_stresser = await guild.create_category("━━━ STRESSER PANEL ━━━", overwrites=over_v)
    await guild.create_text_channel("🔥┃l4-methods", category=cat_stresser)
    await guild.create_text_channel("🌊┃l7-methods", category=cat_stresser)

    cat_admin = await guild.create_category("━━━ ADMIN PANEL ━━━", overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)})
    await guild.create_text_channel("🚫┃ban-list-hwid", category=cat_admin)

    await interaction.followup.send("✅ Gotowe!")

# --- OBSŁUGA WERYFIKACJI ---

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if "weryfikacja" in message.channel.name and message.content.lower() == "accept":
        await message.channel.send(f"✅ {message.author.mention}, podaj swój **Login** oraz **ID urządzenia**, aby powiązać konto:", delete_after=15)
        
        # Nadanie rangi po wpisaniu accept
        role = discord.utils.get(message.guild.roles, name="Verified")
        await message.author.add_roles(role)
        
        # Logowanie weryfikacji
        verified_users[message.author.id] = message.author.name
        print(f"Nowy zweryfikowany: {message.author.name}")
        
        try: await message.delete()
        except: pass

    await bot.process_commands(message)

# --- KOMENDY BLACKLISTY ---

@bot.tree.command(name="bl_add", description="Banuje HWID urządzenia")
@app_commands.checks.has_permissions(administrator=True)
async def bl_add(interaction: discord.Interaction, hwid: str):
    blacklisted_hwids.append(hwid.upper())
    await interaction.response.send_message(f"🚫 Urządzenie `{hwid}` zostało zablokowane.", ephemeral=True)

# --- START ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    if TOKEN:
        bot.run(TOKEN)
