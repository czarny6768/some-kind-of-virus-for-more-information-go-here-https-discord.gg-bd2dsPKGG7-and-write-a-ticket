import discord
from discord import app_commands
import os
from flask import Flask, jsonify
from threading import Thread

# --- SERWER DO SPRAWDZANIA LICENCJI ---
app = Flask('')

# Tu przechowujemy status (uproszczone dla 1 osoby)
# W prawdziwym systemie użylibyśmy bazy danych
authorized_users = [1500513889064980661] # ID Twojej roli Customer

@app.route('/check/<user_id>')
def check_license(user_id):
    # Logika: Bot sprawdza, czy użytkownik o danym ID ma dostęp
    # Na potrzeby testu zwracamy status aktywny
    return jsonify({"status": "active", "msg": "Access Granted"})

def run():
    app.run(host='0.0.0.0', port=10000)

# --- BOT DISCORD ---
class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=1465510011445706892)
        await self.tree.sync(guild=guild)

bot = MyBot()

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
