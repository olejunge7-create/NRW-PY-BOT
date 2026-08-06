import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# Flask-App für Render (damit der Port offen ist)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Discord Bot Setup
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

        await self.tree.sync()
        print("Slash-Befehle erfolgreich synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")

@bot.tree.command(name="setup_panels", description="Sendet die Ticket- und Bewerbungs-Panels in den aktuellen Kanal.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_panels(interaction: discord.Interaction):
    from tickets import TicketView
    from bewerbung import BewerbungView

    await interaction.response.send_message("✅ Panels werden erstellt...", ephemeral=True)
    await interaction.channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())
    await interaction.channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())

if __name__ == "__main__":
    # Flask in einem separaten Thread starten, damit der Bot und der Webserver gleichzeitig laufen
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Bot starten
    bot.run(os.getenv("DISCORD_TOKEN"))