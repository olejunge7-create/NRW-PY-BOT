import discord
from discord.ext import commands

# Deine festen Rollen-IDs von Rang 1 bis 21
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
    1534325338212007986,  # Rang 21
]

class RanksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="uprank", description="Befördert einen Benutzer mit schickem Embed.")
    @discord.app_commands.describe(member="Der Benutzer", new_role="Die neue Rang-Rolle", reason="Grund für die Beförderung")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def uprank(self, interaction: discord.Interaction, member: discord.Member, new_role: discord.Role, reason: str):
        try:
            # Finde die alte Rang-Rolle heraus, bevor wir sie löschen
            old_roles = [r for r in member.roles if r.id in RANK_ROLES]
            old_role_name = old_roles[0].name if old_roles else "Kein Rang"

            # Alte Rollen entfernen & neue geben
            if old_roles:
                await member.remove_roles(*old_roles)
            await member.add_roles(new_role)

            # Embed im gewünschten Design erstellen
            embed = discord.Embed(color=discord.Color.green())
            embed.description = (
                f"╭────────────────────────╮\n"
                f"  📢 **RANGÄNDERUNG**\n"
                f"╰────────────────────────╯\n\n"
                f"👤 **Mitglied:** {member.mention}\n"
                f"📈 **Beförderung**\n\n"
                f"**Alter Rang:** {old_role_name}\n"
                f"➡️ **Neuer Rang:** {new_role.mention}\n\n"
                f"🎉 Herzlichen Glückwunsch! Grund: *{reason}*"
            )
            embed.set_footer(text=f"Durchgeführt von {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rollen zu ändern.", ephemeral=True)

    @discord.app_commands.command(name="downrank", description="Degradiert einen Benutzer mit schickem Embed.")
    @discord.app_commands.describe(member="Der Benutzer", new_role="Die neue Rang-Rolle", reason="Grund für die Degradierung")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def downrank(self, interaction: discord.Interaction, member: discord.Member, new_role: discord.Role, reason: str):
        try:
            old_roles = [r for r in member.roles if r.id in RANK_ROLES]
            old_role_name = old_roles[0].name if old_roles else "Kein Rang"

            if old_roles:
                await member.remove_roles(*old_roles)
            await member.add_roles(new_role)

            embed = discord.Embed(color=discord.Color.red())
            embed.description = (
                f"╭────────────────────────╮\n"
                f"  📢 **RANGÄNDERUNG**\n"
                f"╰────────────────────────╯\n\n"
                f"👤 **Mitglied:** {member.mention}\n"
                f"📉 **Degradierung**\n\n"
                f"**Alter Rang:** {old_role_name}\n"
                f"➡️ **Neuer Rang:** {new_role.mention}\n\n"
                f"⚠️ Grund: *{reason}*"
            )
            embed.set_footer(text=f"Durchgeführt von {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rollen zu ändern.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RanksCog(bot))