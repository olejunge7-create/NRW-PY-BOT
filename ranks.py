import discord
from discord.ext import commands

# Deine Rang-IDs für die automatische Erkennung
RANK_ROLES = [
    1534325338182520991, 1534325338182520992, 1534325338182520993, 1534325338182520994,
    1534325338199556137, 1534325338199556138, 1534325338199556139, 1534325338199556140,
    1534325338199556142, 1534325338199556143, 1534325338199556145, 1534325338199556146,
    1534325338212007978, 1534325338212007979, 1534325338212007980, 1534325338212007981,
    1534325338212007982, 1534325338212007983, 1534325338212007984, 1534325338212007985,
    1534325338212007986
]

class RanksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="uprank", description="Befördert einen User.")
    @discord.app_commands.describe(member="Der User", new_role="Die neue Rolle", reason="Grund")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def uprank(self, interaction: discord.Interaction, member: discord.Member, new_role: discord.Role, reason: str):
        try:
            # Entferne alle alten Rang-Rollen
            roles_to_remove = [r for r in member.roles if r.id in RANK_ROLES]
            await member.remove_roles(*roles_to_remove)
            
            # Neue Rolle geben
            await member.add_roles(new_role)
            await interaction.response.send_message(f"✅ {member.mention} befördert!\n**Neue Rolle:** {new_role.mention}\n**Grund:** {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehler: Keine Berechtigung.", ephemeral=True)

    @discord.app_commands.command(name="downrank", description="Degradiert einen User.")
    @discord.app_commands.describe(member="Der User", new_role="Die neue Rolle", reason="Grund")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def downrank(self, interaction: discord.Interaction, member: discord.Member, new_role: discord.Role, reason: str):
        try:
            # Entferne alle aktuellen Rang-Rollen
            roles_to_remove = [r for r in member.roles if r.id in RANK_ROLES]
            await member.remove_roles(*roles_to_remove)
            
            # Neue Rolle geben
            await member.add_roles(new_role)
            await interaction.response.send_message(f"✅ {member.mention} degradiert.\n**Neue Rolle:** {new_role.mention}\n**Grund:** {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehler: Keine Berechtigung.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RanksCog(bot))