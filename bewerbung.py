import discord
from discord.ext import commands
import asyncio

TEAMLEITUNG_ROLE_ID = 1534325338199556145
BEWERBUNG_LOG_CHANNEL_ID = 1534552376911073451

class BewerbungsEntscheidView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def check_permissions(self, interaction: discord.Interaction) -> bool:
        teamleitung_role = interaction.guild.get_role(TEAMLEITUNG_ROLE_ID)
        is_admin = interaction.user.guild_permissions.administrator
        if is_admin: 
            return True
        if teamleitung_role:
            return any(r.position >= teamleitung_role.position for r in interaction.user.roles)
        return False

    async def get_applicant_user(self, interaction: discord.Interaction):
        # Versucht den Bewerber anhand des Embed-Titels herauszufinden
        embed = interaction.message.embeds[0]
        title = embed.title  # Beispiel: "📝 Neue Bewerbung: Username"
        username = title.split("📝 Neue Bewerbung: ")[-1]
        
        # In der Guild nach dem Member suchen
        for member in interaction.guild.members:
            if member.name == username or member.display_name == username:
                return member
        return None

    @discord.ui.button(label="Annehmen", style=discord.ButtonStyle.green, custom_id="accept_bewerbung", emoji="✅")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message("❌ Nur für Teamleitung!", ephemeral=True)
            return
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.set_field_at(10, name="Status", value=f"✅ Angenommen von {interaction.user.mention}", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Dem Bewerber eine DM schicken
        applicant = await self.get_applicant_user(interaction)
        if applicant:
            try:
                await applicant.send("🎉 **Glückwunsch!** Deine Bewerbung wurde soeben **angenommen**. Das Team wird sich bald bei dir melden.")
            except discord.Forbidden:
                pass

        await interaction.followup.send("Bewerbung angenommen und User benachrichtigt.")

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.red, custom_id="deny_bewerbung", emoji="❌")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message("❌ Nur für Teamleitung!", ephemeral=True)
            return
        
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.set_field_at(10, name="Status", value=f"❌ Abgelehnt von {interaction.user.mention}", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Dem Bewerber eine DM schicken
        applicant = await self.get_applicant_user(interaction)
        if applicant:
            try:
                await applicant.send("❌ Schade! Deine Bewerbung wurde leider **abgelehnt**. Wir wünschen dir dennoch viel Erfolg weiterhin.")
            except discord.Forbidden:
                pass

        await interaction.followup.send("Bewerbung abgelehnt und User benachrichtigt.")

class BewerbungView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Bewerben", style=discord.ButtonStyle.blurple, custom_id="open_bewerbung_dm", emoji="📝")
    async def open_dm_bewerbung(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        await interaction.response.send_message("📬 Check deine DMs! Ich habe dir die Fragen geschickt.", ephemeral=True)

        try:
            dm = await user.create_dm()
            def check(m): return m.author == user and isinstance(m.channel, discord.DMChannel)

            await dm.send("📝 **Team-Bewerbung (10 Fragen)**\nBeantworte bitte nacheinander die folgenden Fragen:")
            
            fragen = [
                ("1/10: Wie ist dein Name?", "name"),
                ("2/10: Wie alt bist du?", "alter"),
                ("3/10: Was sind deine Stärken?", "staerken"),
                ("4/10: Was sind deine Schwächen?", "schwaechen"),
                ("5/10: Hast du Erfahrung als Teammitglied?", "erfahrung"),
                ("6/10: Was würdest du bei einem Regelbruch machen?", "regelbruch"),
                ("7/10: Wie verhältst du dich bei Provokation?", "provokation"),
                ("8/10: Welche Aufgaben im Team interessieren dich am meisten?", "aufgaben"),
                ("9/10: Wie viel Zeit hast du in der Woche?", "zeit"),
                ("10/10: Hast du noch Fragen an uns?", "fragen_an_uns")
            ]

            antworten = {}
            for frage_text, key in fragen:
                await dm.send(f"**{frage_text}**")
                msg = await self.bot.wait_for('message', timeout=600.0, check=check)
                antworten[key] = msg.content

            embed = discord.Embed(title=f"📝 Neue Bewerbung: {user.name}", color=discord.Color.gold())
            for frage_text, key in fragen:
                embed.add_field(name=frage_text, value=antworten[key], inline=False)
            embed.add_field(name="Status", value="⏳ Ausstehend", inline=False)

            log_channel = interaction.guild.get_channel(BEWERBUNG_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=embed, view=BewerbungsEntscheidView())
            
            await dm.send("✅ Deine Bewerbung wurde erfolgreich abgeschickt!")

        except asyncio.TimeoutError:
            await user.send("⏰ Deine Zeit ist abgelaufen. Die Bewerbung wurde abgebrochen.")
        except discord.Forbidden:
            await interaction.followup.send("❌ Ich konnte dir keine DM senden! Bitte aktiviere deine Direktnachrichten.", ephemeral=True)

class BewerbungCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(BewerbungCog(bot))