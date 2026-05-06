import discord
from discord import app_commands
import os
import random
import string
import time
import asyncio
from flask import Flask, jsonify
from threading import Thread
from datetime import datetime, timedelta

# --- KONFIGURACJA SYSTEMU ---
active_tokens = {} 
user_usage = {}   
user_subscriptions = {} # Przechowuje daty wygaśnięcia rang nadanych przez /nadaj

# TWOJE ID RANG (Upewnij się, że te ID są poprawne na Twoim serwerze)
RANKS = {
    1500513889064980661: {"name": "Customer", "limit": 5},
    1500535408147173457: {"name": "Pro", "limit": 10},      
    1500535548438253771: {"name": "Master", "limit": 999999} 
}

# --- SERWER FLASK (API dla Twojej maszynki Titan) ---
app = Flask('')

@app.route('/')
def home():
    return "Beblobo Auth V3 - System Działa"

@app.route('/verify/<user_code>/<discord_id>')
def verify(user_code, discord_id):
    now = time.time()
    if user_code in active_tokens:
        data = active_tokens[user_code]
        if str(data["user_id"]) == str(discord_id):
            if now <= data["expiry"]:
                # Kod poprawny - usuwamy go, by nie użyć go drugi raz
                del active_tokens[user_code]
                return jsonify({"auth": True})
            else:
                return jsonify({"auth": False, "reason": "Kod wygasl"}), 403
    return jsonify({"auth": False, "reason": "Nieprawidlowy kod"}), 403

def run_flask():
    # Render używa portu 10000
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class TitanAuth(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True 
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # Raport statusu wysyłany na kanał co 15 minut
    async def status_monitor_loop(self):
        await self.wait_until_ready()
        LOG_CHANNEL_ID = 1465516223096951026 
        channel = self.get_channel(LOG_CHANNEL_ID)

        while not self.is_closed():
            if channel:
                now = datetime.now().strftime("%H:%M:%S")
                total_tokens = len(active_tokens)
                emb = discord.Embed(
                    title="📡 STATUS SYSTEMU BEBLOBO",
                    description="Serwer autoryzacji pracuje poprawnie.",
                    color=0x2ECC71 
                )
                emb.add_field(name="Ostatnia aktualizacja", value=f"`{now}`")
                emb.add_field(name="Aktywne kody w kolejce", value=f"`{total_tokens}`")
                try:
                    await channel.send(embed=emb)
                except:
                    pass
            await asyncio.sleep(900) 

    async def setup_hook(self):
        guild_id = discord.Object(id=1465510011445706892)
        self.loop.create_task(self.status_monitor_loop())
        
        # --- KOMENDA /NADAJ (Dla Administratora) ---
        @self.tree.command(name="nadaj", description="Nadaje rangę użytkownikowi na określoną ilość dni", guild=guild_id)
        @app_commands.checks.has_permissions(administrator=True)
        async def nadaj(interaction: discord.Interaction, uzytkownik: discord.Member, ranga: discord.Role, dni: int):
            expiry_date = datetime.now() + timedelta(days=dni)
            user_subscriptions[uzytkownik.id] = {"role_id": ranga.id, "expiry": expiry_date}
            
            try:
                await uzytkownik.add_roles(ranga)
                emb = discord.Embed(title="✅ PRZYZNANO DOSTĘP", color=0x2ECC71)
                emb.add_field(name="Użytkownik", value=uzytkownik.mention)
                emb.add_field(name="Ranga", value=ranga.name)
                emb.add_field(name="Czas trwania", value=f"{dni} dni (do {expiry_date.strftime('%Y-%m-%d')})")
                await interaction.response.send_message(embed=emb)
            except:
                await interaction.response.send_message("❌ Błąd: Upewnij się, że rola bota jest wyżej niż nadawana ranga!", ephemeral=True)

        # --- KOMENDA /INFO (Dla każdego) ---
        @self.tree.command(name="info", description="Sprawdza ile dni licencji Ci pozostało", guild=guild_id)
        async def info(interaction: discord.Interaction):
            user_id = interaction.user.id
            sub = user_subscriptions.get(user_id)
            
            emb = discord.Embed(title="ℹ️ TWOJA SUBSKRYPCJA", color=0x3498DB)
            if sub:
                remaining = sub["expiry"] - datetime.now()
                dni = max(0, remaining.days)
                emb.add_field(name="Status", value="✅ Aktywna", inline=True)
                emb.add_field(name="Pozostało dni", value=f"**{dni}**", inline=True)
                emb.add_field(name="Data wygaśnięcia", value=f"`{sub['expiry'].strftime('%Y-%m-%d')}`", inline=False)
            else:
                emb.add_field(name="Status", value="❌ Brak aktywnej subskrypcji czasowej.")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        # --- KOMENDA /LICENCJA (Generowanie kodu) ---
        @self.tree.command(name="licencja", description="Generuje kod 20-sekundowy do maszynki Titan", guild=guild_id)
        async def licencja(interaction: discord.Interaction):
            user_id = interaction.user.id
            
            # Sprawdzanie rangi i limitu
            limit = -1
            r_name = ""
            for role_id, data in RANKS.items():
                if any(role.id == role_id for role in interaction.user.roles):
                    if data["limit"] > limit:
                        limit = data["limit"]
                        r_name = data["name"]

            if limit == -1:
                return await interaction.response.send_message("❌ Nie posiadasz wymaganej rangi, aby generować kody!", ephemeral=True)

            # Limit dzienny
            today = datetime.now().strftime("%Y-%m-%d")
            if user_id not in user_usage or user_usage[user_id]["last_reset"] != today:
                user_usage[user_id] = {"count": 0, "last_reset": today}

            if user_usage[user_id]["count"] >= limit:
                return await interaction.response.send_message(f"❌ Wykorzystałeś dzisiejszy limit ({limit}) dla rangi {r_name}!", ephemeral=True)

            # Generowanie kodu
            code = "BEB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            active_tokens[code] = {"user_id": user_id, "expiry": time.time() + 20}
            user_usage[user_id]["count"] += 1 
            
            emb = discord.Embed(title="🔐 KOD WYGENEROWANY", color=0xFF0000)
            emb.add_field(name="KOD LICENCJI", value=f"**`{code}`**")
            emb.add_field(name="WAŻNOŚĆ", value="⌛ **20 SEKUND**", inline=False)
            emb.set_footer(text="Wklej ten kod szybko do swojej maszynki Titan!")
            
            await interaction.response.send_message(embed=emb, ephemeral=True)

        await self.tree.sync(guild=guild_id)

bot = TitanAuth()

# --- URUCHAMIANIE ---
if __name__ == "__main__":
    # Start serwera Flask w tle
    Thread(target=run_flask).start()
    
    # Pobranie tokena z Environment Variables na hostingu
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        print("🚀 System Beblobo Auth V3 wystartowal poprawnie!")
        bot.run(TOKEN)
    else:
        print("❌ BLAD: Nie znaleziono zmiennej DISCORD_TOKEN w ustawieniach!")
