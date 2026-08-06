import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask
from tickets import TicketView

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
        # Lade deine Module (Dashboard ist komplett raus)
        await bot.load_extension("ranks")
        print("Modul 'ranks' geladen!")

        await bot.load_extension("tickets")
        print("Modul 'tickets' geladen!")

        # Befehle synchronisieren
        SERVER_ID = discord.Object(id=1534325338170065128)
        bot.tree.copy_global_to(guild=SERVER_ID)
        await bot.tree.sync(guild=SERVER_ID)
        print("Befehle synchronisiert!")

        # --- Ticket-Kanal beim Start aufräumen & neu posten ---
        CHANNEL_TICKETS = 1534325339369635991
        chan_tick = bot.get_channel(CHANNEL_TICKETS)
        if chan_tick:
            try:
                # Löscht alte Nachrichten im Ticket-Kanal beim Start
                await chan_tick.purge(limit=10)
                print("Alte Ticket-Nachrichten gelöscht.")
            except Exception as e:
                print(f"Konnte Nachrichten nicht löschen: {e}")
            
            # Frisches Ticket-Panel posten
            embed_tick = discord.Embed(
                title="🎫 TICKET SUPPORT",
                description="Klicke auf den unten stehenden Button, um ein Support-Ticket zu öffnen.",
                color=discord.Color.blue()
            )
            embed_tick.set_footer(text="🤖 Ticket System")
            await chan_tick.send(embed=embed_tick, view=TicketView())
            print("Frisches Ticket-Panel im Kanal gepostet!")

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