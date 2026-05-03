import discord
from discord.ext import commands
from fastapi import FastAPI
import uvicorn
import threading
import os

# --- KONFIGURACJA (UZUPEŁNIJ SWOJE ID) ---
# Token pobierany jest bezpiecznie z ustawień Rendera
TOKEN = os.getenv("DISCORD_TOKEN")

# TUTAJ WPISZ SWOJE NUMERY ID (kliknij PRAWYM na serwer/rangę na Discordzie)
GUILD_ID = 1465510011445706892  # <--- ZMIEŃ NA ID TWOJEGO SERWERA
ROLE_ID = 987654321   # <--- ZMIEŃ NA ID TWOJEJ RANGI (NP. PREMIUM/KLIENT)

# Ustawienia bota
intents = discord.Intents.default()
intents.members = True  # To pozwala botowi sprawdzać rangi
bot = commands.Bot(command_prefix="!", intents=intents)

# Ustawienia API (serwera licencji)
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Beblobo Auth System is Online", "bot_connected": bot.is_ready()}

@app.get("/verify/{user_id}")
async def verify_user(user_id: int):
    # Szukamy Twojego serwera
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return {"status": "error", "message": "Bot nie widzi serwera. Sprawdź GUILD_ID."}
    
    # Szukamy użytkownika na serwerze
    member = guild.get_member(user_id)
    if not member:
        return {"status": "not_found", "message": "Użytkownik nie jest na serwerze."}
    
    # Sprawdzamy czy ma rangę
    has_role = any(role.id == ROLE_ID for role in member.roles)
    
    if has_role:
        return {"status": "success", "access": True, "user": str(member)}
    else:
        return {"status": "denied", "access": False, "message": "Brak wymaganej rangi."}

def run_api():
    # Render sam przypisuje port, musimy go odczytać
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    print(f"✅ System autoryzacji działa na serwerze ID: {GUILD_ID}")

if __name__ == "__main__":
    # Odpalamy serwer WWW w tle
    threading.Thread(target=run_api, daemon=True).start()
    # Odpalamy bota
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ BŁĄD: Brak DISCORD_TOKEN w ustawieniach Environment!")
