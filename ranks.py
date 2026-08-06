import discord
from discord.ext import commands

class RanksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="uprank", description="Gibt einem Benutzer eine Rang-Rolle.")
    @discord.app_commands.describe(member="Der Benutzer, der die Rolle bekommen soll", role="Die auszuwählende Rang-Rolle")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def uprank(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await interaction.response.send_message(f"❌ {member.mention} hat die Rolle {role.mention} bereits!", ephemeral=True)
            return

        try:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Erfolgreich! {member.mention} wurde die Rolle {role.mention} gegeben.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rolle zu vergeben. (Achte darauf, dass die Bot-Rolle in der Server-Liste über dieser Rolle steht).", ephemeral=True)

    @discord.app_commands.command(name="downrank", description="Entfernt eine Rang-Rolle von einem Benutzer.")
    @discord.app_commands.describe(member="Der Benutzer, dem die Rolle entfernt werden soll", role="Die zu entfernende Rolle")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def downrank(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if role not in member.roles:
            await interaction.response.send_message(f"❌ {member.mention} hat die Rolle {role.mention} gar nicht!", ephemeral=True)
            return

        try:
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Erfolgreich! {member.mention} wurde die Rolle {role.mention} entfernt.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rolle zu entfernen.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RanksCog(bot))