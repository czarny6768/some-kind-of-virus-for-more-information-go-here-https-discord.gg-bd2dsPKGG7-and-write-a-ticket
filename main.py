import discord
from discord import app_commands
import os
import time
import hashlib
from flask import Flask
from threading import Thread

# --- KONFIGURACJA TRYBU PRAC TECHNICZNYCH ---
# True = włączone prace techniczne (bot reaguje tylko komunikatem o dev beblobo)
# False = bot działa normalnie
PRACE_TECHNICZNE = True

# --- KONFIGURACJA ZGODNA Z C++ ---
SALT = "TITAN_ULTIMATE_2026"

# --- SERWER WWW DLA RENDERA (Żeby bot nie padł) ---
app = Flask('')
@app.route('/')
def home(): return "Titan Auth Server is Running"
def run_web(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_web).start()

# --- TWOJE ID ---
GUILD_ID = 1465514942340792340           
GEN_ROLE_ID = 1500513889064980661        
MEMBER_ROLE_ID = 1465514942340792340     
TICKET_CATEGORY_ID = 1502371148778836009 

class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if PRACE_TECHNICZNE:
            return await interaction.response.send_message("🛠️ Obecnie trwają prace techniczne dev beblobo.", ephemeral=True)
        await interaction.channel.delete()

class TicketOpen(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.primary, custom_id="open_t")
    async def open_t(self, interaction: discord.Interaction, button: discord.ui.Button):
        if PRACE_TECHNICZNE:
            return await interaction.response.send_message("🛠️ Obecnie trwają prace techniczne dev beblobo.", ephemeral=True)
        
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)
        await ch.send(f"Siema {interaction.user.mention}, napisz w czym problem.", view=TicketControl())

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="✅ Weryfikacja", style=discord.ButtonStyle.success, custom_id="ver_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if PRACE_TECHNICZNE:
            return await interaction.response.send_message("🛠️ Obecnie trwają prace techniczne dev beblobo.", ephemeral=True)
            
        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Nadano rangę!", ephemeral=True)

class TitanBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        self.add_view(TicketOpen()); self.add_view(TicketControl()); self.add_view(VerifyView())
        await self.tree.sync()

bot = TitanBot()

# --- GENERATOR KLUCZA ZGODNY Z TWOIM C++ ---
def generate_titan_key():
    time_window = int(time.time() / 20)
    raw_string = str(time_window) + SALT
    md5_hash = hashlib.md5(raw_string.encode()).hexdigest().upper()
    return f"TITAN-{md5_hash[:8]}"

@bot.tree.command(name="gen", description="Generuje klucz licencyjny do aplikacji C++")
async def gen(interaction: discord.Interaction):
    if PRACE_TECHNICZNE:
        return await interaction.response.send_message("🛠️ Obecnie trwają prace techniczne dev beblobo.", ephemeral=True)

    role = interaction.guild.get_role(GEN_ROLE_ID)
    if role not in interaction.user.roles:
        return await interaction.response.send_message("❌ Nie masz uprawnień!", ephemeral=True)
    
    key = generate_titan_key()
    
    await interaction.response.send_message(
        f"🛡️ **TITAN V12 ULTRA - AUTORYZACJA**\n\n"
        f"🔑 Twój klucz: `{key}`\n"
        f"⏳ Ważność: **20 sekund**\n\n"
        f"Uruchom aplikację C++, wpisz swoje Discord ID i wklej ten klucz."
    )

@bot.tree.command(name="setup", description="Panele bota")
async def setup(interaction: discord.Interaction, typ: str):
    if PRACE_TECHNICZNE:
        return await interaction.response.send_message("🛠️ Obecnie trwają prace techniczne dev beblobo.", ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tylko Admin!", ephemeral=True)
    if typ == "ver":
        await interaction.channel.send("🛡️ **WERYFIKACJA**", view=VerifyView())
    elif typ == "ticket":
        await interaction.channel.send("🎫 **TICKETY**", view=TicketOpen())
    await interaction.response.send_message("Wysłano.", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
