import discord
from discord.ext import commands
import asyncio

# Die 20 Fragen
QUESTIONS = [
    "1. Wie ist dein Vorname?",
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

class BewerbungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Jetzt Bewerben", style=discord.ButtonStyle.primary, custom_id="persistent_bewerbung_start_btn")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        await interaction.response.send_message("✅ Schaue bitte in deine **Direktnachrichten (DMs)**! Die Bewerbung hat dort begonnen.", ephemeral=True)

        try:
            dm_channel = await user.create_dm()
        except discord.Forbidden:
            return

        await dm_channel.send("👋 Hallo! Schön, dass du dich bewirbst. Ich stelle dir jetzt **20 Fragen nacheinander**. Antworte einfach auf jede Nachricht.\n\n**Frage 1 geht los:**")

        answers = []
        
        # Geht jede Frage einzeln durch
        for i, question in enumerate(QUESTIONS):
            await dm_channel.send(f"**[{i+1}/20]** {question}")

            def check(m):
                return m.author == user and isinstance(m.channel, discord.DMChannel)

            try:
                # Wartet auf die Antwort des Users (max. 5 Minuten pro Frage)
                msg = await interaction.client.wait_for('message', check=check, timeout=300.0)
                answers.append(msg.content)
            except asyncio.TimeoutError:
                await dm_channel.send("❌ Die Bewerbung wurde abgebrochen, da du zu lange nicht geantwortet hast.")
                return

        # Wenn alle Fragen beantwortet wurden
        await dm_channel.send("🎉 **Vielen Dank!** Deine Bewerbung wurde erfolgreich abgesendet und an das Team weitergeleitet.")

        # Bewerbung in den Admin-/Auswertungskanal senden (Kanal-ID: 1534552376911073451)
        admin_channel = interaction.client.get_channel(1534552376911073451)
        if admin_channel:
            embed = discord.Embed(
                title=f"📄 Neue Bewerbung von {user.display_name}",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Fügt alle Fragen und Antworten übersichtlich ins Embed ein
            for i in range(len(QUESTIONS)):
                q_text = QUESTIONS[i]
                a_text = answers[i]
                embed.add_field(name=q_text, value=a_text if a_text else "Keine Antwort", inline=False)
            
            await admin_channel.send(embed=embed)

class BewerbungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BewerbungCog(bot))