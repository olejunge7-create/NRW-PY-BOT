import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# Importiere die Views für die Persistenz nach Neustarts
from tickets import TicketView, CloseTicketView
from bewerbung import BewerbungView

# Flask-Server damit Render denkt, es ist ein Web Service mit offenem Port
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

        # WICHTIG: Views beim Start registrieren, damit Buttons nach Neustart nicht ablaufen!
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        self.add_view(BewerbungView())
        print("Persistente Views erfolgreich registriert!")

        # Slash-Befehle synchronisieren
        await self.tree.sync()
        print("Slash-Befehle erfolgreich synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")

@bot.tree.command(name="setup_panels", description="Sendet die Ticket- und Bewerbungs-Panels in den aktuellen Kanal.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_panels(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Panels werden erstellt...", ephemeral=True)
    await interaction.channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())
    await interaction.channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())

if __name__ == "__main__":
    # Flask-Server im Hintergrund starten
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Bot starten
    bot.run(os.getenv("DISCORD_TOKEN"))