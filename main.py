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
    return "TITAN BOT SYSTEM ONLINE"

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

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="TITAN V12 | Professional Setup"))

# --- KOMENDA BUDOWANIA ---

@bot.tree.command(name="setup_server_full", description="Buduje cały serwer z opisami na każdym kanale")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server_full(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("🏗️ Buduję profesjonalny serwer z pełną informacją...", ephemeral=True)

    # 1. Rangi
    customer_role = discord.utils.get(guild.roles, name="Customer") or await guild.create_role(name="Customer", color=discord.Color.blue(), hoist=True)
    admin_role = discord.utils.get(guild.roles, name="Admin") or await guild.create_role(name="Admin", color=discord.Color.red(), hoist=True)

    # Funkcja pomocnicza do wysyłania Info-Embedów
    async def send_info(channel, title, desc):
        embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
        embed.set_footer(text="System Informacyjny TITAN V12")
        await channel.send(embed=embed)

    # --- KATEGORIE I KANAŁY ---

    # 🛡️ WERYFIKACJA
    ch_ver = await guild.create_text_channel("🛡️┃weryfikacja")
    await send_info(ch_ver, "🛡️ SYSTEM WERYFIKACJI", "Przeczytaj regulamin i czekaj na nadanie rangi przez Administratora lub użyj przycisku (jeśli dodasz bota do weryfikacji).")

    # ━━━ INFO ━━━
    cat_info = await guild.create_category("━━━ INFORMACJE ━━━")
    
    ch_desc = await guild.create_text_channel("🚀┃opis-projektu", category=cat_info)
    await send_info(ch_desc, "🚀 O PROJEKCIE", "**TITAN V12** to efekt 5 miesięcy prac. Posiadamy 30,000+ proxy i technologię Ghost-Mode (RAM-only).")
    
    ch_ann = await guild.create_text_channel("📢┃ogłoszenia-ogólne", category=cat_info)
    await send_info(ch_ann, "📢 OGŁOSZENIA", "Tutaj znajdziesz najważniejsze informacje dotyczące przerw technicznych i aktualizacji dla wszystkich.")
    
    ch_price = await guild.create_text_channel("💎┃cennik", category=cat_info)
    await send_info(ch_price, "💎 CENNIK USŁUG", "• Titan V12 (LIFE): 70 PLN\n• Custom Locker: od 100 PLN\n• FUD Malware: od 150 PLN")
    
    ch_vouch = await guild.create_text_channel("✅┃vouch-dowody", category=cat_info)
    await send_info(ch_vouch, "✅ VOUCH / DOWODY", "Tutaj publikujemy potwierdzenia transakcji i opinie klientów. Możesz tu wrzucić swojego voucha po zakupie!")

    # ━━━ USŁUGI ━━━
    cat_serv = await guild.create_category("━━━ USŁUGI PREMIUM ━━━")
    
    ch_lock = await guild.create_text_channel("🔒┃locker-ransom", category=cat_serv)
    await send_info(ch_lock, "🔒 LOCKER / RANSOMWARE", "Usługa tworzenia spersonalizowanych lockerów. Pełne wsparcie i konfiguracja panelu.")
    
    ch_mal = await guild.create_text_channel("🦠┃custom-malware", category=cat_serv)
    await send_info(ch_mal, "🦠 CUSTOM MALWARE", "Tworzymy oprogramowanie pod specjalne zamówienie. Pełen FUD i niewykrywalność.")

    # ━━━ STREFA VIP (Customer) ━━━
    over_cust = {guild.default_role: discord.PermissionOverwrite(read_messages=False), customer_role: discord.PermissionOverwrite(read_messages=True)}
    cat_vip = await guild.create_category("━━━ STREFA VIP ━━━", overwrites=over_cust)
    
    ch_ann_vip = await guild.create_text_channel("📢┃ogłoszenia-klient", category=cat_vip)
    await send_info(ch_ann_vip, "👑 VIP ANNOUNCEMENTS", "Ekskluzywne informacje o nowych funkcjach i aktualizacjach proxy tylko dla klientów.")
    
    ch_down = await guild.create_text_channel("📥┃pobierz-titan", category=cat_vip)
    await send_info(ch_down, "📥 POBIERANIE", "Tutaj zawsze znajdziesz najnowszą, bezpieczną wersję TITAN V12.")
    
    ch_key = await guild.create_text_channel("🔑┃generuj-licencje", category=cat_vip)
    await send_info(ch_key, "🔑 GENERATOR", "Wpisz `/licencja`, aby wygenerować swój unikalny klucz do programu.")

    # ━━━ ADMIN PANEL ━━━
    over_admin = {guild.default_role: discord.PermissionOverwrite(read_messages=False), admin_role: discord.PermissionOverwrite(read_messages=True)}
    cat_admin = await guild.create_category("━━━ ADMIN PANEL ━━━", overwrites=over_admin)
    
    ch_adm_ch = await guild.create_text_channel("🔒┃admin-chat", category=cat_admin)
    await send_info(ch_adm_ch, "🔒 TAJNY CZAT", "Miejsce na wewnętrzne rozmowy administracji.")

    # ━━━ SUPPORT ━━━
    cat_supp = await guild.create_category("━━━ SUPPORT ━━━")
    ch_tick = await guild.create_text_channel("🎫┃otwórz-ticket", category=cat_supp)
    await send_info(ch_tick, "🎫 WSPARCIE", "Masz problem lub chcesz coś kupić? Wpisz `/ticket`, a otworzymy dla Ciebie prywatny kanał.")

    await interaction.followup.send("✅ Serwer został w pełni skonfigurowany z informacjami na każdym kanale!")

# --- POZOSTAŁE KOMENDY ---

@bot.tree.command(name="licencja", description="Generuje klucz (Dla Klientów)")
async def licencja(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    key = hashlib.md5(f"{ts}TITAN_ULTIMATE_2026".encode()).hexdigest().upper()[:8]
    await interaction.response.send_message(f"🔑 Twój klucz: `TITAN-{key}`", ephemeral=True)

@bot.tree.command(name="ticket", description="Otwiera ticket")
async def ticket(interaction: discord.Interaction):
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
    chan = await interaction.guild.create_text_channel(f"🎫-ticket-{interaction.user.name}", overwrites=overwrites)
    await chan.send(f"Witaj {interaction.user.mention}! Czekaj na Admina.")
    await interaction.response.send_message(f"✅ Ticket: {chan.mention}", ephemeral=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    if TOKEN:
        bot.run(TOKEN)
