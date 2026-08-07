import discord
from discord.ext import commands
import os
from flask import Flask
import threading

from tickets import TicketView, CloseTicketView
from bewerbung import BewerbungView

# Flask-Server für Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online!"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        extensions = ["tickets", "bewerbung", "warn", "ranks"]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"{ext}-System erfolgreich geladen!")
            except Exception as e:
                print(f"Fehler beim Laden von {ext}: {e}")

        # Views für Persistenz registrieren
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        self.add_view(BewerbungView())
        print("Persistente Views registriert!")

        await self.tree.sync()
        print("Slash-Befehle synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")
    
    # Deine IDs
    TICKET_CHANNEL_ID = 1534325339369635991
    BEWERBUNG_CHANNEL_ID = 1534579610497581180
    
    # 1. Automatisches Ticket-Panel
    ticket_channel = bot.get_channel(TICKET_CHANNEL_ID)
    if ticket_channel:
        exists = False
        async for message in ticket_channel.history(limit=10):
            if message.author == bot.user and "Support-Ticket" in message.content:
                exists = True
                break
        if not exists:
            await ticket_channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())
            print("Ticket-Panel automatisch gesendet!")

    # 2. Automatisches Bewerbungs-Panel
    bewerbung_channel = bot.get_channel(BEWERBUNG_CHANNEL_ID)
    if bewerbung_channel:
        exists = False
        async for message in bewerbung_channel.history(limit=10):
            if message.author == bot.user and "Team-Bewerbung" in message.content:
                exists = True
                break
        if not exists:
            await bewerbung_channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())
            print("Bewerbungs-Panel automatisch gesendet!")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    bot.run(os.getenv("DISCORD_TOKEN"))