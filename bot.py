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
        # Cogs laden
        try:
            await self.load_extension("tickets")
            print("Ticket-System geladen!")
        except Exception as e:
            print(f"Fehler beim Laden von tickets: {e}")

        try:
            await self.load_extension("bewerbung")
            print("Bewerbungs-System geladen!")
        except Exception as e:
            print(f"Fehler beim Laden von bewerbung: {e}")

        # Slash-Befehle global synchronisieren, damit /setup_panels sofort verfügbar ist
        await self.tree.sync()
        print("Slash-Befehle synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")

# Echter Slash-Befehl: /setup_panels
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
