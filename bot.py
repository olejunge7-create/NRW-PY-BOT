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

# Ticket-Setup mit automatischem Kanal-Clear
@bot.tree.command(name="setup_ticket", description="Leert den Kanal und sendet das Ticket-Panel.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    # Löscht alle Nachrichten im Kanal (bis zu 100 Stück)
    deleted = await interaction.channel.purge(limit=100)
    
    # Sendet das neue Panel
    await interaction.channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())
    await interaction.followup.send(f"✅ Kanal erfolgreich geleert und Ticket-Panel gesendet! ({len(deleted)} alte Nachrichten gelöscht)", ephemeral=True)

# Bewerbungs-Setup mit automatischem Kanal-Clear
@bot.tree.command(name="setup_bewerbung", description="Leert den Kanal und sendet das Bewerbungs-Panel.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_bewerbung(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    # Löscht alle Nachrichten im Kanal (bis zu 100 Stück)
    deleted = await interaction.channel.purge(limit=100)
    
    # Sendet das neue Panel
    await interaction.channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())
    await interaction.followup.send(f"✅ Kanal erfolgreich geleert und Bewerbungs-Panel gesendet! ({len(deleted)} alte Nachrichten gelöscht)", ephemeral=True)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    bot.run(os.getenv("DISCORD_TOKEN"))