import os
import discord
from discord import app_commands
from discord.ext import commands

# Bot-Setup mit Server Members Intent (wichtig für Nicknamen)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"Eingeloggt als {bot.user}")
  try:
    synced = await bot.tree.sync()
    print(f"{len(synced)} Slash-Befehle synchronisiert.")
  except Exception as e:
    print(e)


# --- UPRANK / PROMOTE ---
@bot.tree.command(
    name="promote", description="Befördere ein Teammitglied und setze den Rang-Präfix"
)
@app_commands.describe(
    member="Das Teammitglied",
    rang_name="Das Kürzel für den Namen (z.B. Mod, T-Sup)",
    rolle="Die neue Discord-Rolle",
    grund="Der Grund für den Uprank",
)
async def promote(
    interaction: discord.Interaction,
    member: discord.Member,
    rang_name: str,
    rolle: discord.Role,
    grund: str,
):
  # 1. Rolle vergeben
  await member.add_roles(rolle)

  # 2. Nicknamen anpassen (z.B. "Mod | Username")
  neuer_nickname = f"{rang_name} | {member.name}"
  try:
    await member.edit(nick=neuer_nickname)
  except discord.Forbidden:
    pass  # Falls der Bot keine Rechte hat (z.B. Höherrangiger User)

  # 3. Embed Nachricht erstellen
  embed = discord.Embed(
      title="🚀 Team-Beförderung (Uprank)",
      color=discord.Color.green(),
      timestamp=discord.utils.utcnow(),
  )
  embed.add_field(name="User", value=member.mention, inline=False)
  embed.add_field(name="Neuer Rang / Rolle", value=rolle.mention, inline=False)
  embed.add_field(name="Neues Kürzel", value=rang_name, inline=True)
  embed.add_field(name="Grund", value=grund, inline=False)
  embed.set_footer(text=f"Ausgeführt von {interaction.user.name}")

  await interaction.response.send_message(embed=embed)


# --- DEMOTE / ABSTUFUNG ---
@bot.tree.command(
    name="demote", description="Stufe ein Teammitglied herab und passe den Namen an"
)
@app_commands.describe(
    member="Das Teammitglied",
    neuer_tag="Das neue Kürzel oder '-' (ohne Kürzel)",
    rolle="Die Rolle, die entfernt oder gewechselt wird",
    grund="Der Grund für die Degradierung",
)
async def demote(
    interaction: discord.Interaction,
    member: discord.Member,
    neuer_tag: str,
    rolle: discord.Role,
    grund: str,
):
  # 1. Rolle entfernen
  await member.remove_roles(rolle)

  # 2. Nicknamen anpassen (oder zurücksetzen)
  if neuer_tag.lower() == "keiner" or neuer_tag == "-":
    neuer_nickname = member.name  # Nur der normale Name
  else:
    neuer_nickname = f"{neuer_tag} | {member.name}"

  try:
    await member.edit(nick=neuer_nickname)
  except discord.Forbidden:
    pass

  # 3. Embed Nachricht erstellen
  embed = discord.Embed(
      title="⚠️ Team-Degradierung (Demote)",
      color=discord.Color.red(),
      timestamp=discord.utils.utcnow(),
  )
  embed.add_field(name="User", value=member.mention, inline=False)
  embed.add_field(name="Betroffene Rolle", value=rolle.mention, inline=False)
  embed.add_field(name="Grund", value=grund, inline=False)
  embed.set_footer(text=f"Ausgeführt von {interaction.user.name}")

  await interaction.response.send_message(embed=embed)


# Bot sicher über Render-Umgebungsvariable starten
if __name__ == "__main__":
  bot.run(os.environ["DISCORD_TOKEN"])