import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# Importiere die Views
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
        # Cogs laden
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

        # Slash-Befehle synchronisieren
        await self.tree.sync()
        print("Slash-Befehle synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")

# Neuer Befehl nur für Tickets
@bot.tree.command(name="setup_ticket", description="Sendet das Ticket-Panel.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Ticket-Panel wird erstellt...", ephemeral=True)
    await interaction.channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())

# Neuer Befehl nur für Bewerbungen
@bot.tree.command(name="setup_bewerbung", description="Sendet das Bewerbungs-Panel.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_bewerbung(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Bewerbungs-Panel wird erstellt...", ephemeral=True)
    await interaction.channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    bot.run(os.getenv("DISCORD_TOKEN"))