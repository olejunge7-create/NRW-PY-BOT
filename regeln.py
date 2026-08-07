import discord
from discord.ext import commands

REGEL_CHANNEL_ID = 1534624451662970920

class RegelnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # Wird beim Laden des Cogs ausgeführt und sendet das Regelwerk, falls noch nicht da
        regeln_channel = self.bot.get_channel(REGEL_CHANNEL_ID)
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
                    value="• **Allgemeines:** Mit Betreten akzeptierst du die Regeln. Respekt ist Pflicht. Keine Support-Diskussionen im RP. Bugusing/Bannumgehung verboten.\n• **Roleplay-Pflicht:** Midcore-RP ist Pflicht. RP steht vor dem Gewinnen.\n• **FailRP:** Unrealistische Handlungen, Zweckentfremdung von Ausrüstung/Fahrzeugen und Zerstörung von Situationen verboten.",
                    inline=False
                )
                
                embed.add_field(
                    name="§4 - §6 RDM, VDM & FearRP",
                    value="• **RDM:** Angreifen oder Töten ohne RP-Hintergrund ist verboten.\n• **VDM:** Fahrzeuge dürfen nicht als Waffen oder zum Überfahren genutzt werden (Ausnahme: Lebensgefahr).\n• **FearRP:** Du musst Waffen ernst nehmen, Polizeianweisungen befolgen und bei Lebensgefahr angemessen reagieren.",
                    inline=False
                )
                
                embed.add_field(
                    name="§7 - §9 CrashRP, Combat Logging & Metagaming",
                    value="• **CrashRP:** Unfälle realistisch ausspielen, Verletzungen beachten, Rettungsdienst rufen.\n• **Combat Logging:** Server während Festnahmen, Kontrollen, Verfolgungen oder Schießereien zu verlassen ist verboten.\n• **Metagaming:** OOC-/Discord-/Stream-Infos im RP zu nutzen ist verboten.",
                    inline=False
                )
                
                embed.add_field(
                    name="§10 - §12 PowerRP, NLR & Polizei",
                    value="• **PowerRP:** Andere zu unfairen Handlungen zwingen oder Reaktionen verweigern ist verboten.\n• **NLR:** Nach RP-Tod keine Erinnerung an die Situation und keine sofortige Rückkehr/Rache.\n• **Polizei:** Muss realistisch, verhältnismäßig und gesetzeskonform handeln.",
                    inline=False
                )

                embed.add_field(
                    name="§13 - §16 Rettungsdienst, Feuerwehr, Funk & Fahrzeuge",
                    value="• **Rettungsdienst & Feuerwehr:** Realistisches RP, faire Behandlung, zuständig für Brände, Notrufe.\n• **Funk:** Keine Beleidigungen/Spam, hohe Funkdisziplin.\n• **Fahrzeuge:** Keine absichtlichen Rammaktionen oder mutwillige Zerstörung.",
                    inline=False
                )

                embed.add_field(
                    name="§17 - §20 Trolling, Werbung, Team & Strafen",
                    value="• **Trolling & Werbung:** Stören, Soundboards und Fremdwerbung verboten.\n• **Team:** Anweisungen des Teams sind Folge zu leisten.\n• **Strafen:** Verwarnung, Kick, Temp-Bann oder Permanenter Bann.\n\n*Realistisches und faires Roleplay sorgt für mehr Spielspaß für alle!*",
                    inline=False
                )
                
                await regeln_channel.send(embed=embed)
                print("Regelwerk-Embed automatisch gesendet!")

async def setup(bot):
    await bot.add_cog(RegelnCog(bot))