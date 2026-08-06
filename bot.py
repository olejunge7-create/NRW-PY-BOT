import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask

# --- FLASK WEB SERVER (Für Render Web Service) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- DISCORD BOT SETUP ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user.name} (ID: {bot.user.id})")
    print("Lade Cogs (Module)...")

    try:
        # Lädt das Rang-System (beförderung, degradierung, warn etc.)
        await bot.load_extension("ranks")
        print("Modul 'ranks' erfolgreich geladen!")

        # Lädt das Ticket-System
        await bot.load_extension("tickets")
        print("Modul 'tickets' erfolgreich geladen!")

        # Lädt das neue Team-Dashboard
        await bot.load_extension("daschbord")
        print("Modul 'daschbord' erfolgreich geladen!")

        # --- TRAGE HIER DEINE SERVER-ID EIN (ersetze die 0 durch deine ID) ---
        SERVER_ID = discord.Object(id=1534325338170065128)
        
        bot.tree.copy_global_to(guild=SERVER_ID)
        await bot.tree.sync(guild=SERVER_ID)
        print("Befehle direkt für deinen Server synchronisiert!")
        
    except Exception as e:
        print(f"Fehler beim Laden der Module: {e}")

    print("Bot ist vollständig bereit!")

# --- HAUPTSTART ---
if __name__ == "__main__":
    import threading

    # 1. Starte den Flask-Webserver im Hintergrund-Thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. Starte den Discord Bot
    TOKEN = os.environ.get("DISCORD_TOKEN", "DEIN_DISCORD_BOT_TOKEN_HIER_EIN")

    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Fehler beim Starten des Bots: {e}")