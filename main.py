import discord
from discord import app_commands
from discord.ext import commands
import hashlib
import time
import os

# --- KONFIGURACJA ---
TOKEN = os.getenv('DISCORD_TOKEN')
SALT = "TITAN_ULTIMATE_2026" 

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronizuje komendy slash z serwerem Discord
        await self.tree.sync()
        print(f"Zsynchronizowano komendy slash dla {self.user}")

bot = TitanBot()

def get_md5_short(data):
    return hashlib.md5(data.encode()).hexdigest().upper()[:8]

@bot.tree.command(name="gen", description="Generuje tymczasowy klucz licencyjny Titan V12")
async def gen(interaction: discord.Interaction):
    ts = int(time.time() // 20)
    key_hash = get_md5_short(str(ts) + SALT)
    current_key = f"TITAN-{key_hash}"
    
    embed = discord.Embed(title="🛡️ TITAN V12 - KLUCZ", color=0x00ff00)
    embed.add_field(name="TWÓJ KLUCZ:", value=f"`{current_key}`", inline=False)
    embed.set_footer(text="Pospiesz się! Klucz wygasa za około 20 sekund.")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket", description="Otwiera prywatny kanał wsparcia/zakupu")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    channel_name = f"ticket-{user.name.lower()}"

    # Uprawnienia: Widzi tylko admin (kto ma zarządzanie kanałami) i użytkownik
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    embed = discord.Embed(
        title="🎫 NOWY TICKET", 
        description=f"Witaj {user.mention}! Zaraz ktoś z administracji się Tobą zajmie.", 
        color=0x3498db
    )
    embed.add_field(name="KOMENDA ZAMKNIĘCIA:", value="Użyj `/close`, aby usunąć ten kanał.", inline=False)
    
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Stworzono ticket: {channel.mention}", ephemeral=True)

@bot.tree.command(name="close", description="Zamyka i usuwa aktualny kanał ticketu")
async def close(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("Zamykanie ticketu za 3 sekundy...")
        time.sleep(3)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ Tej komendy możesz użyć tylko na kanale typu ticket!", ephemeral=True)

if TOKEN:
    bot.run(TOKEN)
else:
    print("BŁĄD: Brak DISCORD_TOKEN w zmiennych środowiskowych!")
