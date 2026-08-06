import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Alle Cogs (Tickets, Bewerbung, Warn-System und Ranks) automatisch laden
        extensions = ["tickets", "bewerbung", "warn", "ranks"]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"{ext}-System erfolgreich geladen!")
            except Exception as e:
                print(f"Fehler beim Laden von {ext}: {e}")

        # Slash-Befehle global synchronisieren
        await self.tree.sync()
        print("Slash-Befehle erfolgreich synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")

# Slash-Befehl zum Erstellen der Panels im Kanal
@bot.tree.command(name="setup_panels", description="Sendet die Ticket- und Bewerbungs-Panels in den aktuellen Kanal.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_panels(interaction: discord.Interaction):
    from tickets import TicketView
    from bewerbung import BewerbungView

    # Antwort senden, damit die Interaktion nicht fehlschlägt
    await interaction.response.send_message("✅ Panels werden erstellt...", ephemeral=True)

    # Panels in den Kanal schicken
    await interaction.channel.send("🎫 **Support-Ticket erstellen**\nKlicke auf den Button unten, um ein Ticket zu öffnen:", view=TicketView())
    await interaction.channel.send("📝 **Team-Bewerbung**\nKlicke auf den Button unten, um dich zu bewerben:", view=BewerbungView())

bot.run(os.getenv("DISCORD_TOKEN"))