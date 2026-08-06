import asyncio
import os
import discord
from discord.ext import commands
from flask import Flask
# Importiere Dashboard (Admin) UND UserApplyView (User) aus dashboard.py
from dashboard import DashboardView, UserApplyView
from tickets import TicketView

# --- FLASK WEB SERVER (Für Render) ---
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
        await bot.load_extension("ranks")
        await bot.load_extension("tickets")
        await bot.load_extension("dashboard")
        print("Alle Module geladen!")

        SERVER_ID = discord.Object(id=1534325338170065128)
        bot.tree.copy_global_to(guild=SERVER_ID)
        await bot.tree.sync(guild=SERVER_ID)
        print("Befehle synchronisiert!")

        # --- 1. USER: BEWERBUNG (1534579610497581180) ---
        CHANNEL_USER_BEWERBEN = 1534579610497581180
        chan_user = bot.get_channel(CHANNEL_USER_BEWERBEN)
        if chan_user:
            try: await chan_user.purge(limit=10)
            except: pass
            
            embed_user = discord.Embed(
                title="👋 Werde Teil unseres Teams!",
                description="Klicke auf den Button unten, um das Bewerbungsformular zu öffnen. Fülle alle Felder wahrheitsgemäß aus.",
                color=discord.Color.gold()
            )
            embed_user.set_footer(text="Wir freuen uns auf dich!")
            await chan_user.send(embed=embed_user, view=UserApplyView())

        # --- 2. ADMIN: DASHBOARD (1534552376911073451) ---
        CHANNEL_ADMIN_DASHBOARD = 1534552376911073451
        chan_admin = bot.get_channel(CHANNEL_ADMIN_DASHBOARD)
        if chan_admin:
            try: await chan_admin.purge(limit=10)
            except: pass
            
            embed_dash = discord.Embed(
                title="🛡️ TEAM DASHBOARD",
                description="Hier landen neue Bewerbungen. Mit den Buttons kannst du diese annehmen oder ablehnen.",
                color=discord.Color.blurple()
            )
            embed_dash.set_footer(text="System Dashboard")
            await chan_admin.send(embed=embed_dash, view=DashboardView())

        # --- 3. USER: TICKETS (1534325339369635991) ---
        CHANNEL_TICKETS = 1534325339369635991
        chan_tick = bot.get_channel(CHANNEL_TICKETS)
        if chan_tick:
            try: await chan_tick.purge(limit=10)
            except: pass
            
            embed_tick = discord.Embed(
                title="🎫 TICKET SUPPORT",
                description="Klicke auf den Button, um ein Support-Ticket zu öffnen.",
                color=discord.Color.blue()
            )
            await chan_tick.send(embed=embed_tick, view=TicketView())

    except Exception as e:
        print(f"Fehler: {e}")

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
        print(f"Fehler beim Start: {e}")