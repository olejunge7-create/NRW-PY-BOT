import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask
from tickets import TicketView
from bewerbung import BewerbungView

# --- FLASK WEB SERVER ---
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
        # Module laden
        await bot.load_extension("tickets")
        await bot.load_extension("bewerbung")
        print("Modul 'tickets' & 'bewerbung' geladen!")

        # Befehle synchronisieren
        SERVER_ID = discord.Object(id=1534325338170065128)
        bot.tree.copy_global_to(guild=SERVER_ID)
        await bot.tree.sync(guild=SERVER_ID)
        print("Befehle synchronisiert!")

        # --- 1. Ticket-Kanal aufräumen & neu posten ---
        CHANNEL_TICKETS = 1534325339369635991
        chan_tick = bot.get_channel(CHANNEL_TICKETS)
        if chan_tick:
            try:
                await chan_tick.purge(limit=10)
            except Exception:
                pass
            
            embed_tick = discord.Embed(
                title="🎫 TICKET SUPPORT",
                description="Klicke auf den unten stehenden Button, um ein Support-Ticket zu öffnen.",
                color=discord.Color.blue()
            )
            embed_tick.set_footer(text="🤖 Ticket System")
            await chan_tick.send(embed=embed_tick, view=TicketView())

        # --- 2. Bewerbungs-Kanal aufräumen & neu posten ---
        CHANNEL_BEWERBUNG = 1534579610497581180
        chan_bew = bot.get_channel(CHANNEL_BEWERBUNG)
        if chan_bew:
            try:
                await chan_bew.purge(limit=10)
            except Exception:
                pass
            
            embed_bew = discord.Embed(
                title="📝 TEAM BEWERBUNG",
                description="Möchtest du ein Teil unseres Teams werden? Klicke auf den Button unten, um dich zu bewerben!",
                color=discord.Color.gold()
            )
            embed_bew.set_footer(text="🤖 Bewerbungs System")
            await chan_bew.send(embed=embed_bew, view=BewerbungView())

    except Exception as e:
        print(f"Fehler beim Start: {e}")

    print("Bot ist vollständig bereit!")

if __name__ == "__main__":
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    TOKEN = os.environ.get("DISCORD_TOKEN", "DEIN_DISCORD_BOT_TOKEN_HIER_EIN")
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Fehler beim Starten des Bots: {e}")