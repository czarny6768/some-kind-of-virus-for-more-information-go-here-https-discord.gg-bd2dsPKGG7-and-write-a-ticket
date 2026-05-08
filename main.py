import discord
from discord import app_commands, ui
from discord.ext import commands
import os, threading, hashlib, time, requests
from flask import Flask, jsonify, request

# --- KONFIGURACJA ---
app = Flask('')
WEBHOOK_URL = "https://discord.com/api/webhooks/1502378413179277506/_YBOofVZk0ArSieyz0uarZNJ8m7PpOT7BsiKhFdHOaxVe2Hzf_rhoRmLEBwYrBs4ycda"
SALT = "TITAN_V12_SECRET_2026"
blacklisted_hwids = ["BAN-123"]

# Najmocniejsze proxy SOCKS5
PROXY_LINKS = {
    "mala": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "duza": "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
}

# Funkcja wysyłająca powiadomienia na Twój Webhook
def log_to_webhook(content):
    data = {"content": content}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass

# --- API DLA C++ ---
@app.route('/check_auth', methods=['GET'])
def check_auth():
    user_hwid = request.args.get('hwid', 'Unknown')
    size = request.args.get('size', 'mala')
    
    if user_hwid.upper() in blacklisted_hwids:
        log_to_webhook(f"⚠️ **PRÓBA WEJŚCIA:** Zablokowany użytkownik (HWID: `{user_hwid}`) próbował odpalić program.")
        return jsonify({"status": "banned"}), 403
    
    return jsonify({
        "status": "ok", 
        "proxy_link": PROXY_LINKS.get(size, PROXY_LINKS["mala"])
    }), 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- BOT DISCORD ---
TOKEN = os.environ.get("DISCORD_TOKEN")

class TicketModal(ui.Modal, title='Panel Wsparcia TITAN'):
    subject = ui.TextInput(label='Temat', placeholder='W czym problem?')
    desc = ui.TextInput(label='Opis', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f'ticket-{interaction.user.name}', overwrites=overwrites)
        
        # Logowanie otwarcia ticketu na Webhook
        log_to_webhook(f"🎫 **NOWY TICKET:** Użytkownik {interaction.user.name} otworzył sprawę: `{self.subject.value}`")
        
        await channel.send(f"Witaj {interaction.user.mention}, administracja zaraz Ci pomoże.\n**Temat:** {self.subject.value}\n**Opis:** {self.desc.value}")
        await interaction.response.send_message(f"Otwarto ticket: {channel.mention}", ephemeral=True)

class TitanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    async def setup_hook(self):
        await self.tree.sync()

bot = TitanBot()

@bot.tree.command(name="licencja", description="Klucz 20s dla rangi Customer")
async def licencja(interaction: discord.Interaction):
    if not any(role.name == "Customer" for role in interaction.user.roles):
        await interaction.response.send_message("❌ Nie jesteś w grupie Customer!", ephemeral=True)
        return
    
    t_step = int(time.time() // 20)
    key = hashlib.md5(f"{t_step}{SALT}".encode()).hexdigest().upper()[:8]
    formatted_key = f"TITAN-{key}"
    
    log_to_webhook(f"🔑 **GENEROWANIE:** Użytkownik {interaction.user.name} wygenerował klucz sesji.")
    await interaction.response.send_message(f"✅ Twój klucz (ważny 20s): `{formatted_key}`", ephemeral=True)

@bot.tree.command(name="ticket", description="Zgłoś problem do administracji")
async def ticket(interaction: discord.Interaction):
    await interaction.response.send_modal(TicketModal())

@bot.tree.command(name="bl_add", description="Banowanie HWID (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def bl_add(interaction: discord.Interaction, hwid: str):
    blacklisted_hwids.append(hwid.upper())
    log_to_webhook(f"🚫 **BLACKLIST:** Admin {interaction.user.name} zbanował HWID: `{hwid}`")
    await interaction.response.send_message(f"Zbanowano HWID: `{hwid}`", ephemeral=True)

@bot.event
async def on_ready():
    print(f"TITAN BOT GOTOWY: {bot.user}")
    log_to_webhook("✅ **SYSTEM ONLINE:** Bot i serwer API zostały uruchomione pomyślnie.")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
