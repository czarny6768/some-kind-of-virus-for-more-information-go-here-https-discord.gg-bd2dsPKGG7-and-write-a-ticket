import discord
from discord import app_commands
from discord.ext import commands, tasks
import time
import os
import threading
import hashlib
from flask import Flask

# --- KONFIGURACJA FLASK ---
app = Flask('')

@app.route('/')
def home():
    return "TITAN BOT ONLINE"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- KONFIGURACJA BOTA ---
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="TITAN V12"))

# --- KOMENDA: FULL SETUP SERWERA ---

@bot.tree.command(name="setup_server", description="Buduje kompletny serwer TITAN V12")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Generowanie profesjonalnego serwera...", ephemeral=True)

    # 1. Tworzenie rangi Customer (jeśli nie istnieje)
    customer_role = discord.utils.get(guild.roles, name="Customer")
    if not customer_role:
        customer_role = await guild.create_role(name="Customer", color=discord.Color.blue(), hoist=True)

    # 2. Kategorie i kanały
    
    # --- INFO ---
    cat_info = await guild.create_category("━━ INFO ━━")
    ch_reg = await guild.create_text_channel("📜┃regulamin", category=cat_info)
    ch_ann = await guild.create_text_channel("📢┃ogłoszenia", category=cat_info)
    ch_price = await guild.create_text_channel("💎┃cennik", category=cat_info)

    # --- DLA KLIENTÓW (Tylko dla rangi Customer) ---
    overwrites_cust = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        customer_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    cat_cust = await guild.create_category("━━ CUSTOMER ZONE ━━", overwrites=overwrites_cust)
    await guild.create_text_channel("📥┃pobierz-titan", category=cat_cust)
    await guild.create_text_channel("🔑┃generuj-klucz", category=cat_cust)
    await guild.create_text_channel("💬┃czat-vip", category=cat_cust)

    # --- WSPARCIE ---
    cat_supp = await guild.create_category("━━ SUPPORT ━━")
    ch_tick = await guild.create_text_channel("🎫┃odbierz-dostęp", category=cat_supp)

    # 3. Wysyłanie gotowych treści (Embedy)

    # Embed Cennik
    embed_p = discord.Embed(title="💎 CENNIK TITAN V12", color=discord.Color.gold())
    embed_p.add_field(name="TITAN 24H", value="`FREE` (Zrób zadanie na TikToku)", inline=False)
    embed_p.add_field(name="TITAN WEEKLY", value="`20 PLN / 5 EUR`", inline=False)
    embed_p.add_field(name="TITAN LIFETIME", value="`60 PLN / 15 EUR` (Best Deal!)", inline=False)
    embed_p.set_footer(text="Płatności: PSC, BLIK, PayPal, Crypto")
    await ch_price.send(embed=embed_p)

    # Embed Ticket
    embed_t = discord.Embed(title="🎫 ZAKUP LUB DARMOWY DOSTĘP", 
                          description="Otwórz ticket wpisując `/ticket`, aby:\n- Wysłać dowód z TikToka (Free 24h)\n- Kupić wersję Premium", 
                          color=discord.Color.green())
    await ch_tick.send(embed=embed_t)

    await interaction.followup.send("✅ Serwer skonfigurowany pomyślnie!")

# --- POZOSTAŁE KOMENDY ---

@bot.tree.command(name="licencja", description="Generuje klucz (Dla Customer)")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    key = hashlib.md5(f"{ts}TITAN_ULTIMATE_2026".encode()).hexdigest().upper()[:8]
    await interaction.response.send_message(f"🔑 Twój klucz: `TITAN-{key}`", ephemeral=True)

@bot.tree.command(name="ticket", description="Otwiera ticket wsparcia")
async def ticket(interaction: discord.Interaction):
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    chan = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
    await chan.send(f"Witaj {interaction.user.mention}! Opisz swoją sprawę lub wrzuć screena.")
    await interaction.response.send_message(f"✅ Ticket otwarty: {chan.mention}", ephemeral=True)

# --- START ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    if TOKEN:
        bot.run(TOKEN)
