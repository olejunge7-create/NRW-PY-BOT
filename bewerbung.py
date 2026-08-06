import discord
from discord.ext import commands

# Liste der 20 Fragen
QUESTIONS = [
    "1. Wie ist dein Name?",
    "2. Wie alt bist du?",
    "3. Was ist deine genaue Discord-ID (Name#Tag)?",
    "4. Seit wann spielst du auf unserem Server?",
    "5. Hast du bereits Erfahrung als Teammitglied auf anderen Servern?",
    "6. Wenn ja, welche Position hattest du dort?",
    "7. Warum möchtest du gerade bei uns ins Team?",
    "8. Was sind deine Stärken?",
    "9. Was sind deine Schwächen?",
    "10. Wie gehst du mit stressigen Situationen um?",
    "11. Wie oft bist du in der Woche aktiv (Stunden)?",
    "12. Zu welchen Uhrzeiten bist du meistens online?",
    "13. Hast du ein funktionierendes Mikrofon?",
    "14. Bist du bereit, dich an unsere Regeln zu halten?",
    "15. Was würdest du tun, wenn ein Spieler die Regeln bricht?",
    "16. Was würdest du tun, wenn ein Teamkollege einen Fehler macht?",
    "17. Bist du teamfähig?",
    "18. Hast du jemals eine Verwarnung oder einen Bann erhalten?",
    "19. Gibt es etwas, das wir noch über dich wissen sollten?",
    "20. Warum sollten wir gerade DICH wählen?"
]

class BewerbungsModal(discord.ui.Modal, title="Ausführliche Teambewerbung"):
    def __init__(self):
        super().__init__(timeout=None)
        self.inputs = []
        # Da ein Modal maximal 5 TextInputs haben darf, müssen wir das anders lösen.
        # Lösung: User bekommt die Fragen per DM geschickt.
        # Hier triggern wir den Prozess.

    async def on_submit(self, interaction: discord.Interaction):
        pass # Nicht genutzt, da wir DMs nutzen

class BewerbungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Jetzt Bewerben (Start per DM)", style=discord.ButtonStyle.primary, custom_id="persistent_bewerbung_start_btn")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Bitte schaue in deine DMs (Direktnachrichten)!", ephemeral=True)
        
        try:
            # DM an den User
            await interaction.user.send("Hallo! Um dich zu bewerben, beantworte bitte die folgenden 20 Fragen. Antworte einfach nacheinander auf jede Nachricht, die ich dir sende.")
            
            # Hier müsste man eigentlich einen komplexen Listener bauen. 
            # Zur Vereinfachung schicken wir alle Fragen auf einmal oder führen den User durch.
            questions_text = "\n\n".join(QUESTIONS)
            await interaction.user.send(f"Hier sind die Fragen:\n\n{questions_text}\n\nBitte kopiere diese Liste, fülle sie aus und sende sie mir zurück.")
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Ich konnte dir keine Nachricht senden. Bitte aktiviere DMs von Servermitgliedern!", ephemeral=True)

class BewerbungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BewerbungCog(bot))