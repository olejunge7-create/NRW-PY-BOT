import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask

# --- FLASK WEB SERVER (Fuer Render Web Service) ---
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


def run_flask():
  port = int(os.environ.get("PORT", 5000))
  # use_reloader=False ist wichtig, damit Flask sich nicht doppelt startet
  app.run(host="0.0.0.0", port=port, use_reloader=False)


# --- DISCORD BOT SETUP ---
intents = discord.Intents.default()
intents.members = (
    True  # Wichtig, damit Mitglieder, Rollen und Nicknames verwaltet werden können
)
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Eingeloggt als {bot.user.name} (ID: {bot.user.id})")
  print("Lade Cogs...")

  # Lädt automatisch die ranks.py aus demselben Verzeichnis
  try:
    await bot.load_extension("ranks")
    print("Modul 'ranks' erfolgreich geladen!")
  except Exception as e:
    print(f"Fehler beim Laden von ranks: {e}")

  print("Bot ist vollstaendig bereit!")


# --- HAUPTSTART ---
if __name__ == "__main__":
  import threading

  # 1. Starte den Flask-Webserver im Hintergrund-Thread (verhindert den Render Port-Timeout)
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()

  # 2. Starte den Discord Bot (holt den Token sicher aus den Render-Umgebungsvariablen)
  TOKEN = os.environ.get("DISCORD_TOKEN", "DEIN_DISCORD_BOT_TOKEN_HIER_EIN")

  try:
    bot.run(TOKEN)
  except Exception as e:
    print(f"Fehler beim Starten des Bots: {e}")