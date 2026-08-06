import discord
from discord import app_commands
from discord.ext import commands

# Alle 21 Rollen-IDs des Rang-Systems
RANK_ROLES = [
    1534325338182520991,  # Rang 1
    1534325338182520992,  # Rang 2
    1534325338182520993,  # Rang 3
    1534325338182520994,  # Rang 4
    1534325338199556137,  # Rang 5
    1534325338199556138,  # Rang 6
    1534325338199556139,  # Rang 7
    1534325338199556140,  # Rang 8
    1534325338199556142,  # Rang 9
    1534325338199556143,  # Rang 10
    1534325338199556145,  # Rang 11
    1534325338199556146,  # Rang 12
    1534325338212007978,  # Rang 13
    1534325338212007979,  # Rang 14
    1534325338212007980,  # Rang 15
    1534325338212007981,  # Rang 16
    1534325338212007982,  # Rang 17
    1534325338212007983,  # Rang 18
    1534325338212007984,  # Rang 19
    1534325338212007985,  # Rang 20
    1534325338212007986   # Rang 21
]

class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_rank_embed(self, member: discord.Member, typ: str, alter_rang: str, neue_rolle: discord.Role, grund: str, ausfuehrer: discord.Member) -> discord.Embed:
        if typ == "promote":
            title_text = "📈 **Beförderung**"
            desc_text = "🎉 Herzlichen Glückwunsch! Aufgrund deiner Aktivität und deines Engagements wurdest du befördert.\nViel Erfolg in deiner neuen Position! 🚀"
            color = discord.Color.green()
        else:
            title_text = "📉 **Degradierung**"
            desc_text = "⚠️ Dein Rang auf dem Server wurde angepasst.\nWir hoffen, dich bald wieder oben zu sehen!"
            color = discord.Color.red()

        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━╮\n📢 RANGÄNDERUNG\n╰━━━━━━━━━━━━━━━━━━━━━━━╯",
            description=(
                f"👤 **Mitglied:** {member.mention}\n"
                f"{title_text}\n\n"
                f"**Alter Rang:** {alter_rang}\n"
                f"➡️ **Neuer Rang:** {neue_rolle.name}\n"
                f"📝 **Grund:** {grund}\n"
                f"🛡️ **Durchgeführt von:** {ausfuehrer.mention}\n\n"
                f"{desc_text}"
            ),
            color=color
        )
        embed.set_footer(text="🤖 System")
        return embed

    async def _change_rank(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str, typ: str):
        if neue_rolle.id not in RANK_ROLES:
            await interaction.response.send_message("⚠️ Die angegebene Rolle ist keine gültige Rang-Rolle!", ephemeral=True)
            return

        # Alter Rang ermitteln und alte Rang-Rollen entfernen
        alter_rang_name = "Kein Rang"
        for role in member.roles:
            if role.id in RANK_ROLES:
                alter_rang_name = role.name
                if role.id != neue_rolle.id:
                    await member.remove_roles(role)

        # Neue Rolle zuweisen
        await member.add_roles(neue_rolle)

        # Embed erstellen & im Kanal senden
        embed = self.create_rank_embed(member, typ, alter_rang_name, neue_rolle, grund, interaction.user)
        await interaction.response.send_message(embed=embed)

        # Nachricht per Privatnachricht (DM) senden
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    # Vorübergehend umbenannt zu /befoerdern, um den Discord-Cache zu zwingen
    @app_commands.command(name="befoerdern", description="Befördere ein Mitglied auf eine gewählte Rang-Rolle")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def befoerdern(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
        await self._change_rank(interaction, member, neue_rolle, grund, "promote")

    # /demote @member @neue_rolle grund
    @app_commands.command(name="demote", description="Degradiere ein Mitglied auf eine gewählte Rang-Rolle")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def demote(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
        await self._change_rank(interaction, member, neue_rolle, grund, "demote")

    # /drang @member @neue_rolle grund
    @app_commands.command(name="drang", description="Degradiere ein Mitglied (D-Rang) auf eine gewählte Rang-Rolle")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def drang(self, interaction: discord.Interaction, member: discord.Member, neue_rolle: discord.Role, grund: str):
        await self._change_rank(interaction, member, neue_rolle, grund, "demote")

    # /warn @member grund
    @app_commands.command(name="warn", description="Verwarne ein Mitglied auf dem Server")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, grund: str):
        embed = discord.Embed(
            title="╭━━━━━━━━━━━━━━━━━━━━━━━╮\n⚠️ VERWARNUNG\n╰━━━━━━━━━━━━━━━━━━━━━━━╯",
            description=(
                f"👤 **Mitglied:** {member.mention}\n"
                f"📝 **Grund:** {grund}\n"
                f"🛡️ **Verwarnt von:** {interaction.user.mention}\n\n"
                f"Bitte halte dich an die Serverregeln, um weitere Sanktionen zu vermeiden."
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="🤖 Moderation System")

        await interaction.response.send_message(embed=embed)

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

async def setup(bot):
    await bot.add_cog(RankSystem(bot))