import discord
from discord import app_commands
from discord.ext import commands

# Alle 21 Rollen-IDs deines Rang-Systems
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


class Ranks(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  # --- UPRANK / PROMOTE ---
  @app_commands.command(
      name="promote",
      description="Befördere ein Teammitglied und setze den Rang-Präfix",
  )
  @app_commands.describe(
      member="Das Teammitglied",
      rang_name="Das Kürzel für den Namen (z.B. Mod, T-Sup)",
      neue_rolle="Die neue Rang-Rolle",
      grund="Der Grund für den Uprank",
  )
  @app_commands.checks.has_permissions(manage_roles=True, manage_nicknames=True)
  async def promote(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      rang_name: str,
      neue_rolle: discord.Role,
      grund: str,
  ):
    await interaction.response.defer(thinking=True)

    # Alte Rang-Rollen aus der Liste entfernen, damit niemand zwei hat
    roles_to_remove = [
        interaction.guild.get_role(r_id)
        for r_id in RANK_ROLES
        if interaction.guild.get_role(r_id) in member.roles
    ]

    try:
      if roles_to_remove:
        await member.remove_roles(*roles_to_remove)
      await member.add_roles(neue_rolle)
    except discord.Forbidden:
      await interaction.followup.send(
          "❌ Der Bot hat keine Berechtigung, diese Rollen zu verändern!",
          ephemeral=True,
      )
      return

    # Nicknamen anpassen
    neuer_nickname = f"{rang_name} | {member.name}"
    try:
      await member.edit(nick=neuer_nickname)
    except discord.Forbidden:
      pass

    embed = discord.Embed(
        title="🚀 Team-Beförderung (Uprank)",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(
        name="Neuer Rang / Rolle", value=neue_rolle.mention, inline=False
    )
    embed.add_field(name="Neues Kürzel", value=rang_name, inline=True)
    embed.add_field(name="Grund", value=grund, inline=False)
    embed.set_footer(text=f"Ausgeführt von {interaction.user.name}")

    await interaction.followup.send(embed=embed)

  # --- DEMOTE / ABSTUFUNG ---
  @app_commands.command(
      name="demote",
      description="Stufe ein Teammitglied herab und passe den Namen an",
  )
  @app_commands.describe(
      member="Das Teammitglied",
      neuer_tag="Das neue Kürzel oder '-' (ohne Kürzel)",
      neue_rolle="Die neue Rolle nach der Abstufung",
      grund="Der Grund für die Degradierung",
  )
  @app_commands.checks.has_permissions(manage_roles=True, manage_nicknames=True)
  async def demote(
      self,
      interaction: discord.Interaction,
      member: discord.Member,
      neuer_tag: str,
      neue_rolle: discord.Role,
      grund: str,
  ):
    await interaction.response.defer(thinking=True)

    roles_to_remove = [
        interaction.guild.get_role(r_id)
        for r_id in RANK_ROLES
        if interaction.guild.get_role(r_id) in member.roles
    ]

    try:
      if roles_to_remove:
        await member.remove_roles(*roles_to_remove)
      await member.add_roles(neue_rolle)
    except discord.Forbidden:
      await interaction.followup.send(
          "❌ Der Bot hat keine Berechtigung, diese Rollen zu verändern!",
          ephemeral=True,
      )
      return

    if neuer_tag.lower() == "keiner" or neuer_tag == "-":
      neuer_nickname = member.name
    else:
      neuer_nickname = f"{neuer_tag} | {member.name}"

    try:
      await member.edit(nick=neuer_nickname)
    except discord.Forbidden:
      pass

    embed = discord.Embed(
        title="⚠️ Team-Degradierung (Demote)",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Neue Rolle", value=neue_rolle.mention, inline=False)
    embed.add_field(name="Grund", value=grund, inline=False)
    embed.set_footer(text=f"Ausgeführt von {interaction.user.name}")

    await interaction.followup.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Ranks(bot))