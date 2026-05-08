import discord
from discord import app_commands
from discord.ext import commands, tasks
import time
import os
import threading
import hashlib
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "TITAN BOT ONLINE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN = os.environ.get("DISCORD_TOKEN")

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Zsynchronizowano komendy slash.")

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="TITAN V12 | 5 Months of Dev"))

# --- KOMENDA: MEGA SETUP ---

@bot.tree.command(name="setup_server", description="Buduje kompletny serwer z podziałem ogłoszeń")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🛠️ Buduję profesjonalną strukturę serwera...", ephemeral=True)

    # 1. Rangi
    customer_role = discord.utils.get(guild.roles, name="Customer") or await guild.create_role(name="Customer", color=discord.Color.blue(), hoist=True)
    admin_role = discord.utils.get(guild.roles, name="Admin") or await guild.create_role(name="Admin", color=discord.Color.red(), hoist=True)

    # 2. Kanał Weryfikacja
    await guild.create_text_channel("🛡️┃weryfikacja")

    # 3. Kategorie i kanały
    
    # --- INFO & PUBLIC ---
    cat_info = await guild.create_category("━━━ INFO ━━━")
    ch_desc = await guild.create_text_channel("🚀┃opis-projektu", category=cat_info)
    ch_ann_pub = await guild.create_text_channel("📢┃ogłoszenia-ogólne", category=cat_info)
    ch_price = await guild.create_text_channel("💎┃cennik", category=cat_info)
    ch_vouch = await guild.create_text_channel("✅┃vouch-dowody", category=cat_info)

    # --- USŁUGI ---
    cat_services = await guild.create_category("━━━ SERVICES ━━━")
    await guild.create_text_channel("🔒┃locker-ransom", category=cat_services)
    await guild.create_text_channel("🦠┃custom-malware", category=cat_services)
    await guild.create_text_channel("💀┃stealer-setup", category=cat_services)

    # --- CUSTOMER ZONE (Tylko dla Rangi Customer) ---
    overwrites_cust = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        customer_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)
    }
    cat_cust = await guild.create_category("━━━ CUSTOMER ZONE ━━━", overwrites=overwrites_cust)
    await guild.create_text_channel("📢┃ogłoszenia-klient", category=cat_cust)
    await guild.create_text_channel("📥┃download-titan", category=cat_cust)
    await guild.create_text_channel("🔑┃generuj-klucz", category=cat_cust)
    await guild.create_text_channel("💬┃czat-vip", category=cat_cust)

    # --- ADMIN PANEL ---
    overwrites_admin = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        admin_role: discord.PermissionOverwrite(read_messages=True)
    }
    cat_admin = await guild.create_category("━━━ ADMIN PANEL ━━━", overwrites=overwrites_admin)
    await guild.create_text_channel("🔒┃admin-chat", category=cat_admin)

    # --- SUPPORT ---
    cat_supp = await guild.create_category("━━━ SUPPORT ━━━")
    await guild.create_text_channel("🎫┃otwórz-ticket", category=cat_supp)

    # 4. Wysyłanie Treści (Embedy)

    # Opis projektu
    embed_desc = discord.Embed(title="🚀 TITAN NETWORK V12 - O PROJEKCIE", color=discord.Color.blue())
    embed_desc.description = (
        "**TITAN V12** to owoc **5 miesięcy pracy** deweloperów.\n\n"
        "🟢 **Baza Proxy:** 30,000+ aktywnych węzłów Ghost-Proxy.\n"
        "🟢 **Technologia:** Działanie w RAM (Ghost-Mode), brak śladów na dysku.\n"
        "🟢 **Status:** Najwyższy poziom niewykrywalności (FUD)."
    )
    await ch_desc.send(embed=embed_desc)

    # Powitanie w Ogłoszeniach Publicznych
    await ch_ann_pub.send("🔔 **Witaj w ogłoszeniach ogólnych!** Tutaj znajdziesz info o promocjach i nowych usługach.")

    # 5. Cennik
    embed_p = discord.Embed(title="💎 CENNIK", color=discord.Color.gold())
    embed_p.add_field(name="Titan 24H", value="`FREE` (Zrób zadanie)", inline=False)
    embed_p.add_field(name="Custom Locker", value="`od 100 PLN`", inline=False)
    await ch_price.send(embed=embed_p)

    await interaction.followup.send("✅ Serwer TITAN ze strefą Customer został zbudowany!")

# --- POZOSTAŁE KOMENDY ---

@bot.tree.command(name="licencja", description="Generuje klucz (Dla Klientów)")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    key = hashlib.md5(f"{ts}TITAN_ULTIMATE_2026".encode()).hexdigest().upper()[:8]
    await interaction.response.send_message(f"🔑 Twój klucz: `TITAN-{key}`", ephemeral=True)

@bot.tree.command(name="ticket", description="Otwiera ticket")
async def ticket(interaction: discord.Interaction):
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), 
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    chan = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
    await chan.send(f"Witaj {interaction.user.mention}! Opisz swoją sprawę.")
    await interaction.response.send_message(f"✅ Ticket: {chan.mention}", ephemeral=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    if TOKEN:
        bot.run(TOKEN)
