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

    @discord.app_commands.command(name="uprank", description="Stuft einen Benutzer automatisch in den nächsten Rang hoch.")
    @discord.app_commands.describe(member="Der Benutzer, der hochgestuft werden soll")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def uprank(self, interaction: discord.Interaction, member: discord.Member):
        guild = interaction.guild
        user_roles = [r.id for r in member.roles]

        # Finde heraus, welchen aktuellen Rang aus der Liste der User hat
        current_rank_idx = -1
        for i, role_id in enumerate(RANK_ROLES):
            if role_id in user_roles:
                current_rank_idx = i

        # Wenn der User noch keinen Rang hat, geben wir ihm Rang 1
        if current_rank_idx == -1:
            next_role_id = RANK_ROLES[0]
        elif current_rank_idx < len(RANK_ROLES) - 1:
            # Nächsten Rang nehmen
            next_role_id = RANK_ROLES[current_rank_idx + 1]
        else:
            await interaction.response.send_message(f"❌ {member.mention} hat bereits den höchsten Rang (Rang 21) erreicht!", ephemeral=True)
            return

        next_role = guild.get_role(next_role_id)
        if not next_role:
            await interaction.response.send_message("❌ Fehler: Die Rollen-ID wurde auf diesem Server nicht gefunden.", ephemeral=True)
            return

        try:
            # Alten Rang entfernen (falls vorhanden) und neuen geben
            if current_rank_idx != -1:
                old_role = guild.get_role(RANK_ROLES[current_rank_idx])
                if old_role and old_role in member.roles:
                    await member.remove_roles(old_role)

            await member.add_roles(next_role)
            await interaction.response.send_message(f"✅ {member.mention} wurde erfolgreich auf **{next_role.name}** hochgestuft!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rollen zu ändern (Bot-Rolle muss höher stehen).", ephemeral=True)

    @discord.app_commands.command(name="downrank", description="Stuft einen Benutzer einen Rang herunter.")
    @discord.app_commands.describe(member="Der Benutzer, der herabgestuft werden soll")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def downrank(self, interaction: discord.Interaction, member: discord.Member):
        guild = interaction.guild
        user_roles = [r.id for r in member.roles]

        current_rank_idx = -1
        for i, role_id in enumerate(RANK_ROLES):
            if role_id in user_roles:
                current_rank_idx = i

        if current_rank_idx <= 0:
            await interaction.response.send_message(f"❌ {member.mention} hat keinen abstufbaren Rang mehr.", ephemeral=True)
            return

        old_role = guild.get_role(RANK_ROLES[current_rank_idx])
        prev_role = guild.get_role(RANK_ROLES[current_rank_idx - 1])

        try:
            if old_role in member.roles:
                await member.remove_roles(old_role)
            if prev_role:
                await member.add_roles(prev_role)

            await interaction.response.send_message(f"✅ {member.mention} wurde auf **{prev_role.name if prev_role else 'den vorherigen Rang'}** herabgestuft.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Berechtigungen, diese Rollen zu ändern.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RanksCog(bot))