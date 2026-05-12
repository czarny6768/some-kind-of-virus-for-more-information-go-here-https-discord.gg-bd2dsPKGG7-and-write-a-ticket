import discord
from discord import app_commands
import os
import random
import string
from flask import Flask
from threading import Thread

# --- SERWER WWW DLA RENDERA ---
app = Flask('')

@app.route('/')
def home():
    return "Titan V12 is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- TWOJE ZAKTUALIZOWANE ID ---
GUILD_ID = 1465514942340792340           
GEN_ROLE_ID = 1500513889064980661        # Ranga do /gen
MEMBER_ROLE_ID = 1465514942340792340     # Ranga weryfikacji
TICKET_CATEGORY_ID = 1502371148778836009 # NOWE POPRAWNE ID KATEGORII

# --- SYSTEM TICKETÓW ---
class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Usuwanie ticketu...")
        await interaction.channel.delete()

class TicketOpen(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.primary, custom_id="open_t")
    async def open_t(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message(f"❌ Błąd: ID `{TICKET_CATEGORY_ID}` nie wskazuje na kategorię!", ephemeral=True)

        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            ch = await guild.create_text_channel(name=f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
            await interaction.response.send_message(f"✅ Otwarto ticket: {ch.mention}", ephemeral=True)
            await ch.send(f"Siema {interaction.user.mention}, napisz w czym problem.", view=TicketControl())
        except Exception as e:
            await interaction.response.send_message(f"❌ Błąd: {e}", ephemeral=True)

# --- SYSTEM WERYFIKACJI ---
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Weryfikacja", style=discord.ButtonStyle.success, custom_id="ver_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Nadano rangę!", ephemeral=True)

class TitanBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(TicketOpen())
        self.add_view(TicketControl())
        self.add_view(VerifyView())
        await self.tree.sync()

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'✅ Titan Bot online: {bot.user}')

# --- KOMENDA /GEN (JEDNORAZOWY KOD) ---
@bot.tree.command(name="gen", description="Generuje jednorazowy kod dostępu")
async def gen(interaction: discord.Interaction):
    role = interaction.guild.get_role(GEN_ROLE_ID)
    if role not in interaction.user.roles:
        return await interaction.response.send_message("❌ Brak rangi!", ephemeral=True)
    
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    final_code = f"TITAN-{code[:4]}-{code[4:]}"
    await interaction.response.send_message(f"🚀 **KOD:** `{final_code}`")

# --- KOMENDA /SETUP ---
@bot.tree.command(name="setup", description="Panele bota")
@app_commands.choices(typ=[
    app_commands.Choice(name="Weryfikacja", value="ver"),
    app_commands.Choice(name="Ticket", value="ticket")
])
async def setup(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tylko Admin!", ephemeral=True)
    
    if typ.value == "ver":
        await interaction.channel.send("🛡️ **WERYFIKACJA**", view=VerifyView())
    elif typ.value == "ticket":
        await interaction.channel.send("🎫 **TICKETY**", view=TicketOpen())
    await interaction.response.send_message("Wysłano.", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
