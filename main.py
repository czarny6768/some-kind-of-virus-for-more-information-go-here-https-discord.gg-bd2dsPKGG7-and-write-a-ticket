import discord
from discord import app_commands
import os

# --- TWOJE ZAKTUALIZOWANE ID ---
GUILD_ID = 1465514942340792340           
GEN_ROLE_ID = 1500513889064980661        # Ranga do /gen
MEMBER_ROLE_ID = 1465514942340792340     # Ranga nadawana przez weryfikację
TICKET_CATEGORY_ID = 1502371150401900545 # Kategoria ticketów

# --- SYSTEM TICKETÓW (PRZYCISKI) ---
class TicketControl(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zamknij Ticket", style=discord.ButtonStyle.danger, custom_id="close_t")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Usuwanie kanału za 3 sekundy...")
        await interaction.channel.delete()

class TicketOpen(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.primary, custom_id="open_t")
    async def open_t(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ch = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}", 
            category=category, 
            overwrites=overwrites
        )
        
        await interaction.response.send_message(f"✅ Otwarto ticket: {ch.mention}", ephemeral=True)
        await ch.send(f"Siema {interaction.user.mention}, opisz sprawę. Admin zaraz tu będzie.", view=TicketControl())

# --- SYSTEM WERYFIKACJI ---
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Weryfikacja", style=discord.ButtonStyle.success, custom_id="ver_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Nadano rangę członek!", ephemeral=True)
        else:
            await interaction.response.send_message("Błąd: Nie znaleziono roli weryfikacji.", ephemeral=True)

# --- GŁÓWNA KLASA BOTA ---
class TitanBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Rejestracja widoków, aby przyciski działały po restarcie bota
        self.add_view(TicketOpen())
        self.add_view(TicketControl())
        self.add_view(VerifyView())
        await self.tree.sync()

bot = TitanBot()

@bot.event
async def on_ready():
    print(f'✅ TITAN BOT ONLINE: {bot.user}')

# --- KOMENDA /GEN ---
@bot.tree.command(name="gen", description="Uruchamia sesję Titan V12")
async def gen(interaction: discord.Interaction, cel: str, port: int, czas: int):
    role = interaction.guild.get_role(GEN_ROLE_ID)
    if role not in interaction.user.roles:
        return await interaction.response.send_message("❌ Nie masz uprawnień (brak rangi Titan)!", ephemeral=True)
    
    await interaction.response.send_message(f"🚀 **TITAN V12** | Cel: `{cel}` | Port: `{port}` | Czas: `{czas}s`")

# --- KOMENDA /SETUP ---
@bot.tree.command(name="setup", description="Rozstawianie paneli na serwerze")
@app_commands.choices(typ=[
    app_commands.Choice(name="Weryfikacja", value="ver"),
    app_commands.Choice(name="Ticket", value="ticket")
])
async def setup(interaction: discord.Interaction, typ: app_commands.Choice[str]):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Tylko dla Admina!", ephemeral=True)

    if typ.value == "ver":
        await interaction.channel.send("🛡️ **WERYFIKACJA**\nKliknij przycisk poniżej, aby otrzymać rangę członek.", view=VerifyView())
    elif typ.value == "ticket":
        await interaction.channel.send("🎫 **POMOC**\nMasz sprawę do administracji? Otwórz ticket.", view=TicketOpen())
    
    await interaction.response.send_message("Panel wysłany pomyślnie.", ephemeral=True)

# --- URUCHOMIENIE (Hosting) ---
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ BŁĄD: Brak zmiennej DISCORD_TOKEN w ustawieniach hostingu!")
