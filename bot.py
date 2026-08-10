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
intents.dm_messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        extensions = ["tickets", "bewerbung", "warn", "ranks", "regeln", "fraktionen", "partner"]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"{ext}-System erfolgreich geladen!")
            except Exception as e:
                print(f"Fehler beim Laden von {ext}: {e}")

        # Views registrieren
        self.add_view(TicketView())
        self.add_view(CloseTicketView())
        self.add_view(BewerbungView(self))
        print("Persistente Views registriert!")

        await self.tree.sync()
        print("Slash-Befehle synchronisiert!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Eingeloggt als {bot.user}!")
    
    TICKET_CHANNEL_ID = 1534325339369635991
    BEWERBUNG_CHANNEL_ID = 1534579610497581180
    REGEL_CHANNEL_ID = 1534624451662970920
    
    # 1. Automatisches Ticket-Panel
    ticket_channel = bot.get_channel(TICKET_CHANNEL_ID)
    if ticket_channel:
        exists = False
        async for message in ticket_channel.history(limit=10):
            if message.embeds and message.embeds[0].title == "🎟️ NRW RP Tickets":
                exists = True
                break
        if not exists:
            embed = discord.Embed(
                title="🎟️ NRW RP Tickets",
                description="Wähle eine Kategorie aus, um ein Ticket zu erstellen.\n\n• Support & Fragen\n• Team-Bewerbungen\n• Partner-Anfragen\n• Sonstiges",
                color=discord.Color.purple()
            )
            await ticket_channel.send(embed=embed, view=TicketView())
            print("Ticket-Panel automatisch gesendet!")

    # 2. Automatisches Bewerbungs-Panel
    bewerbung_channel = bot.get_channel(BEWERBUNG_CHANNEL_ID)
    if bewerbung_channel:
        exists = False
        async for message in bewerbung_channel.history(limit=10):
            if message.embeds and message.embeds[0].title == "📝 Team-Bewerbungen":
                exists = True
                break
        if not exists:
            embed = discord.Embed(
                title="📝 Team-Bewerbungen",
                description="Möchtest du Teil unseres Teams werden?\n\n• Klicke auf den Button unten\n• Beantworte die Fragen direkt im privaten Chat (DM)",
                color=discord.Color.blue()
            )
            await bewerbung_channel.send(embed=embed, view=BewerbungView(bot))
            print("Bewerbungs-Panel automatisch gesendet!")

    # 3. Automatisches Regelwerk-Embed
    regeln_channel = bot.get_channel(REGEL_CHANNEL_ID)
    if regeln_channel:
        exists = False
        async for message in regeln_channel.history(limit=10):
            if message.embeds and message.embeds[0].title == "📜 Notruf Emden – Regelwerk":
                exists = True
                break
        if not exists:
            embed = discord.Embed(
                title="📜 Notruf Emden – Regelwerk",
                description="**Willkommen auf Notruf Emden – Midcore Roleplay!**\nHier ist unser offizielles Regelwerk. Bitte lies es dir sorgfältig durch.",
                color=discord.Color.from_rgb(0, 150, 255)
            )
            
            embed.add_field(
                name="§1 - §3 Allgemeines & RP-Pflicht & FailRP",
                value="• **Allgemeines:** Mit Betreten akzeptierst du die Regeln. Respekt ist Pflicht. Keine Support-Diskussionen im RP. Bugusing verboten.\n• **Roleplay-Pflicht:** Midcore-RP ist Pflicht. RP steht vor dem Gewinnen.\n• **FailRP:** Unrealistische Handlungen und Zerstörung von Situationen verboten.",
                inline=False
            )
            embed.add_field(
                name="§4 - §6 RDM, VDM & FearRP",
                value="• **RDM:** Angreifen oder Töten ohne RP-Hintergrund ist verboten.\n• **VDM:** Fahrzeuge dürfen nicht als Waffen genutzt werden.\n• **FearRP:** Du musst Waffen ernst nehmen und bei Lebensgefahr reagieren.",
                inline=False
            )
            embed.add_field(
                name="§7 - §9 CrashRP, Combat Logging & Metagaming",
                value="• **CrashRP:** Unfälle realistisch ausspielen, Rettungsdienst rufen.\n• **Combat Logging:** Server während Situationen zu verlassen ist verboten.\n• **Metagaming:** OOC-/Discord-Infos im RP zu nutzen ist verboten.",
                inline=False
            )
            embed.add_field(
                name="§10 - §12 PowerRP, NLR & Polizei",
                value="• **PowerRP:** Andere zu unfairen Handlungen zwingen verboten.\n• **NLR:** Nach RP-Tod keine Erinnerung oder sofortige Rückkehr.\n• **Polizei:** Muss realistisch und verhältnismäßig handeln.",
                inline=False
            )
            embed.add_field(
                name="§13 - §16 Rettungsdienst, Feuerwehr, Funk & Fahrzeuge",
                value="• **Rettungsdienst & Feuerwehr:** Realistisches RP, faire Behandlung.\n• **Funk:** Hohe Funkdisziplin einhalten.\n• **Fahrzeuge:** Keine absichtlichen Rammaktionen.",
                inline=False
            )
            embed.add_field(
                name="§17 - §20 Trolling, Werbung, Team & Strafen",
                value="• **Trolling & Werbung:** Stören und Fremdwerbung verboten.\n• **Team:** Anweisungen sind Folge zu leisten.\n• **Strafen:** Verwarnung, Kick, Temp-Bann oder Permanenter Bann.\n\n*Realistisches Roleplay sorgt für mehr Spielspaß!*",
                inline=False
            )
            
            await regeln_channel.send(embed=embed)
            print("Regelwerk-Embed automatisch gesendet!")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    bot.run(os.getenv("DISCORD_TOKEN"))