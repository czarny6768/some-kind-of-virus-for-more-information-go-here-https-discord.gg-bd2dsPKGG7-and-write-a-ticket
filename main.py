import discord
from discord import app_commands
from discord.ext import commands
import requests
import json
import random
import string
import os  # Dodano do obsługi zmiennych środowiskowych

# --- KONFIGURACJA ---
# Token jest teraz pobierany bezpiecznie z hostingu
TOKEN = os.environ.get("DISCORD_TOKEN")
RENDER_URL = "https://twoja-strona.onrender.com"
ADMIN_ROLE_ID = 123456789012345678  # Zmień na ID Twojej roli Admina

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizacja komend slash przy starcie
        await self.tree.sync()
        print(f"Zsynchronizowano komendy slash dla {self.user}")

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    await bot.change_presence(activity=discord.Streaming(name="TITAN V2 MONITOR", url="https://twitch.tv/"))

# --- KOMENDY SLASH (/) ---

@bot.tree.command(name="genkey", description="Generuje nowy klucz licencyjny (Tylko Admin)")
@app_commands.describe(ranga="Ranga dla klucza (np. USER, VIP, MASTER)")
async def genkey(interaction: discord.Interaction, ranga: str = "USER"):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Brak uprawnień!", ephemeral=True)
        return

    key = "TITAN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    embed = discord.Embed(title="🔑 WYGENEROWANO NOWY KLUCZ", color=discord.Color.green())
    embed.add_field(name="Klucz", value=f"``` {key} ```", inline=False)
    embed.add_field(name="Ranga", value=f"`{ranga}`", inline=True)
    embed.set_footer(text=f"Przez: {interaction.user.name}")
    
    await interaction.response.send_message(f"✅ Klucz wygenerowany. Sprawdź DM.", ephemeral=True)
    try:
        await interaction.user.send(embed=embed)
    except:
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="wl", description="Dodaje użytkownika do Białej Listy (HWID + Nick)")
@app_commands.describe(hwid="Unikalny identyfikator sprzętu", dc_nick="Nick użytkownika na Discordzie")
async def wl(interaction: discord.Interaction, hwid: str, dc_nick: str):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Brak uprawnień!", ephemeral=True)
        return

    payload = {
        "hwid": hwid,
        "username": dc_nick,
        "added_by": interaction.user.name
    }
    
    await interaction.response.defer() # Informujemy Discorda, że przetwarzamy dane
    try:
        r = requests.post(f"{RENDER_URL}/whitelist/add", json=payload, timeout=5)
        
        embed = discord.Embed(title="✅ DODANO DO WHITELIST", color=discord.Color.blue())
        embed.add_field(name="HWID", value=f"```{hwid}```", inline=False)
        embed.add_field(name="Użytkownik DC", value=f"**{dc_nick}**", inline=True)
        embed.set_footer(text=f"Zatwierdził: {interaction.user.name}")
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Błąd połączenia z API na Renderze: {e}")

@bot.tree.command(name="unwl", description="Usuwa HWID z Białej Listy")
@app_commands.describe(hwid="HWID do usunięcia")
async def unwl(interaction: discord.Interaction, hwid: str):
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⛔ Brak uprawnień!", ephemeral=True)
        return

    await interaction.response.defer()
    try:
        r = requests.delete(f"{RENDER_URL}/whitelist/remove/{hwid}", timeout=5)
        await interaction.followup.send(f"🗑️ HWID `{hwid}` został usunięty z listy.")
    except Exception as e:
        await interaction.followup.send(f"❌ Błąd podczas usuwania: {e}")

@bot.tree.command(name="server", description="Sprawdza status serwera TITAN")
async def server(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        r = requests.get(f"{RENDER_URL}/", timeout=5)
        if r.status_code == 200:
            await interaction.followup.send("🟢 **TITAN API:** Online & Secure")
        else:
            await interaction.followup.send(f"🔴 **TITAN API:** Błąd {r.status_code}")
    except:
        await interaction.followup.send("🔴 **TITAN API:** Offline (Render odpoczywa?)")

@bot.tree.command(name="help", description="Lista komend TITAN V2")
async def help_titan(interaction: discord.Interaction):
    embed = discord.Embed(title="🛸 TITAN V2 - SYSTEM DOWODZENIA", color=discord.Color.purple())
    embed.add_field(name="/genkey", value="Generuje licencję (Admin).", inline=False)
    embed.add_field(name="/wl", value="Dodaje HWID i Nick do WL (Admin).", inline=False)
    embed.add_field(name="/unwl", value="Usuwa dostęp dla HWID (Admin).", inline=False)
    embed.add_field(name="/server", value="Status połączenia z Render.", inline=False)
    embed.set_footer(text="Używaj komend z rozwagą.")
    await interaction.response.send_message(embed=embed)

# Sprawdzanie czy token został poprawnie wczytany przed startem
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ BŁĄD: Nie znaleziono zmiennej DISCORD_TOKEN w ustawieniach hostingu!")
