import os
import discord
from discord import app_commands
import random
import string
import json
from datetime import datetime

# --- KONFIGURACJA ---
TOKEN = os.getenv("DISCORD_TOKEN")
# ID Twojego serwera
GUILD_ID = 1465510011445706892 

# ID RANG I ICH LIMITY DZIENNE
ROLES_CONFIG = {
    1500535548438253771: {"name": "master", "limit": 999999}, # Bez limitu
    1500535408147173457: {"name": "pro", "limit": 5},          # Przykład: 5 na dzień
    1500513889064980661: {"name": "customer", "limit": 2}      # Przykład: 2 na dzień
}

class TitanGen(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True # Wymagane do sprawdzania rang
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = TitanGen()

# --- FUNKCJE BAZY DANYCH ---
def get_db():
    if not os.path.exists("database.json"): return {"keys": {}, "usage": {}}
    with open("database.json", "r") as f:
        try: return json.load(f)
        except: return {"keys": {}, "usage": {}}

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

@bot.event
async def on_ready():
    print(f'✅ GENERATOR GOTOWY | {bot.user}')

@bot.tree.command(name="licencja", description="Generuje klucz na podstawie Twojej rangi")
async def licencja(interaction: discord.Interaction):
    user = interaction.user
    db = get_db()
    
    # 1. Sprawdzanie rangi użytkownika
    user_role_id = None
    role_info = None
    
    # Szukamy najwyższej rangi jaką ma użytkownik z listy dozwolonych
    for r_id in ROLES_CONFIG:
        if discord.utils.get(user.roles, id=r_id):
            user_role_id = r_id
            role_info = ROLES_CONFIG[r_id]
            break

    if not role_info:
        await interaction.response.send_message("❌ Nie masz rangi Customer, Pro lub Master, aby wygenerować klucz!", ephemeral=True)
        return

    # 2. Sprawdzanie limitu dziennego
    today = datetime.now().strftime("%Y-%m-%d")
    u_id_str = str(user.id)
    
    if u_id_str not in db["usage"]:
        db["usage"][u_id_str] = {"date": today, "count": 0}
    
    # Reset limitu jeśli jest nowy dzień
    if db["usage"][u_id_str]["date"] != today:
        db["usage"][u_id_str] = {"date": today, "count": 0}

    # Sprawdzenie czy limit został przekroczony
    if db["usage"][u_id_str]["count"] >= role_info["limit"]:
        await interaction.response.send_message(f"❌ Wykorzystałeś już swój dzienny limit ({role_info['limit']}) dla rangi {role_info['name']}!", ephemeral=True)
        return

    # 3. Generowanie klucza
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    key = f"{role_info['name']}-{suffix}"

    # 4. Zapis do bazy
    db["keys"][key] = role_info["name"]
    db["usage"][u_id_str]["count"] += 1
    save_db(db)

    # 5. Odpowiedź
    embed = discord.Embed(title="🔑 KLUCZ WYGENEROWANY", color=0xFF00FF)
    embed.add_field(name="Klucz", value=f"`{key}`", inline=False)
    embed.add_field(name="Ranga", value=role_info["name"].upper(), inline=True)
    embed.add_field(name="Dzisiejsze użycie", value=f"{db['usage'][u_id_str]['count']}/{role_info['limit']}", inline=True)
    embed.set_footer(text="System Titan V2")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(TOKEN)
