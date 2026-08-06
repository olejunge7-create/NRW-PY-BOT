import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask
from dashboard import DashboardView  # Importiert das Dashboard-Panel
from tickets import TicketView       # Importiert das Ticket-Panel

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
        # 1. Cogs laden
        await bot.load_extension("ranks")
        print("Modul 'ranks' erfolgreich geladen!")

        await bot.load_extension("tickets")
        print("Modul 'tickets' erfolgreich geladen!")

        await bot.load_extension("dashboard")
        print("Modul 'dashboard' erfolgreich geladen!")

        # 2. Befehle für den Server synchronisieren
        SERVER_ID = discord.Object(id=1534325338170065128)
        bot.tree.copy_global_to(guild=SERVER_ID)
        await bot.tree.sync(guild=SERVER_ID)
        print("Befehle direkt für deinen Server synchronisiert!")

        # 3. Kanäle beim Start aufräumen und Panels neu posten
        CHANNEL_TICKETS = 1534325339369635991
        CHANNEL_BEWERBUNG = 1534579610497581180
        
        # --- Bewerbungs-Panel erneuern ---
        chan_bew = bot.get_channel(CHANNEL_BEWERBUNG)
        if chan_bew:
            try:
                await chan_bew.purge(limit=10)
            except Exception as e:
                print(f"Konnte Bewerbungs-Nachrichten nicht löschen: {e}")
            
            embed_bew = discord.Embed(
                title="🛡️ TEAM DASHBOARD",
                description=(
                    "Willkommen im zentralen Steuerungs-Panel deines Servers.\n\n"
                    "Wähle eine Option über die unteren Buttons aus:\n"
                    "• **Bewerbung annehmen**\n"
                    "• **Bewerbung ablehnen**"
                ),
                color=discord.Color.blurple()
            )
            embed_bew.set_footer(text="🤖 System Dashboard")
            await chan_bew.send(embed=embed_bew, view=DashboardView())
            print("Bewerbungs-Panel erfolgreich im Kanal aktualisiert!")

        # --- Ticket-Panel erneuern ---
        chan_tick = bot.get_channel(CHANNEL_TICKETS)
        if chan_tick:
            try:
                await chan_tick.purge(limit=10)
            except Exception as e:
                print(f"Konnte Ticket-Nachrichten nicht löschen: {e}")
            
            embed_tick = discord.Embed(
                title="🎫 TICKET SUPPORT",
                description="Klicke auf den unteren Button, um ein neues Support-Ticket zu öffnen.",
                color=discord.Color.blue()
            )
            embed_tick.set_footer(text="🤖 Ticket System")
            await chan_tick.send(embed=embed_tick, view=TicketView())
            print("Ticket-Panel erfolgreich im Kanal aktualisiert!")

    except Exception as e:
        print(f"Fehler beim Start-Vorgang: {e}")

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