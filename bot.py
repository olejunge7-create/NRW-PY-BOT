import os
import discord
import threading
from discord import app_commands
from discord.ext import commands
from flask import Flask

# ==========================================
# 0. FLASK WEBSERVER FÜR 24/7 HOSTER
# ==========================================
app = Flask('')


@app.route('/')
def home():
  return "Bot läuft 24/7!"


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = threading.Thread(target=run)
  t.start()


# ==========================================
# 1. DEINE EINSTELLUNGEN
# ==========================================
# Trage hier zur Sicherheit deinen Token ein: "DEIN_TOKEN_HIER"
TOKEN = os.getenv("TOKEN") or "DEIN_TOKEN_HIER"

TEAM_ROLE_ID = 1534325338182520990
LOG_CHANNEL_ID = 1534552376911073451
ACCEPTED_ROLE_ID = 1534325338182520990
GUILD_ID = 1534445714019450981

FRAGEN = [
    "1. Wie alt bist du?",
    "2. Wie heißt du ingame und wie sollen wir dich nennen?",
    "3. Aus welchem Land/welcher Zeitzone kommst du?",
    "4. Wie viel Erfahrung hast du bereits in diesem Bereich?",
    "5. Warum möchtest du dich genau bei uns bewerben?",
    "6. Wie viele Stunden pro Woche kannst du aktiv sein?",
    "7. Zu welchen Uhrzeiten bist du meistens online?",
    "8. Hast du ein funktionierendes Mikrofon für Discord-Talks?",
    "9. Was sind deine größten Stärken?",
    "10. Was sind deine Schwächen?",
    "11. Wie reagierst du auf Kritik?",
    "12. Wie gehst du mit Konflikten im Team um?",
    "13. Hast du bereits Moderations- oder Team-Erfahrung?",
    "14. Auf welchen Plattformen bist du sonst noch erreichbar?",
    "15. Kennst du bereits Mitglieder unseres Teams?",
    "16. Warum sollten wir dich anderen Bewerbern vorziehen?",
    "17. Was erwartest du von unserem Server / Team?",
    "18. Gibt es Zeiten, in denen du längere Zeit inaktiv sein wirst?",
    "19. Bestätigst du, dass alle Angaben der Wahrheit entsprechen? (Ja/Nein)",
    "20. Möchtest du uns noch etwas zum Abschluss mitteilen?",
]

# ==========================================
# 2. BOT SETUP & INTENTS
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# 3. BUTTONS FÜR TEAM (ANNEHMEN / ABLEHNEN)
# ==========================================
class ReviewView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Annehmen",
      style=discord.ButtonStyle.green,
      custom_id="approve_btn",
  )
  async def approve(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not any(role.id == TEAM_ROLE_ID for role in interaction.user.roles):
      await interaction.response.send_message(
          "Du hast keine Berechtigung, diese Bewerbung zu bearbeiten.",
          ephemeral=True,
      )
      return

    embed = interaction.message.embeds[0]

    try:
      user_id = int(embed.title.split("(")[-1].replace(")", ""))
      guild = interaction.guild
      member = guild.get_member(user_id) or await guild.fetch_member(user_id)
    except Exception:
      member = None

    if member:
      role = guild.get_role(ACCEPTED_ROLE_ID)
      if role:
        await member.add_roles(role)

      try:
        await member.send(
            f"🎉 **Herzlichen Glückwunsch!** Deine Bewerbung auf **{guild.name}**"
            f" wurde von {interaction.user.mention} **angenommen**!"
        )
      except discord.Forbidden:
        pass

    embed.color = discord.Color.green()
    embed.set_footer(text=f"Angenommen von {interaction.user.display_name}")

    for child in self.children:
      child.disabled = True

    await interaction.response.edit_message(embed=embed, view=self)
    await interaction.followup.send(
        f"Die Bewerbung wurde von {interaction.user.mention} **angenommen**."
    )

  @discord.ui.button(
      label="Ablehnen", style=discord.ButtonStyle.red, custom_id="deny_btn"
  )
  async def deny(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not any(role.id == TEAM_ROLE_ID for role in interaction.user.roles):
      await interaction.response.send_message(
          "Du hast keine Berechtigung, diese Bewerbung zu bearbeiten.",
          ephemeral=True,
      )
      return

    embed = interaction.message.embeds[0]

    try:
      user_id = int(embed.title.split("(")[-1].replace(")", ""))
      guild = interaction.guild
      member = guild.get_member(user_id) or await guild.fetch_member(user_id)
    except Exception:
      member = None

    if member:
      try:
        await member.send(
            f"Hallo! Deine Bewerbung auf **{guild.name}** wurde leider"
            " **abgelehnt**."
        )
      except discord.Forbidden:
        pass

    embed.color = discord.Color.red()
    embed.set_footer(text=f"Abgelehnt von {interaction.user.display_name}")

    for child in self.children:
      child.disabled = True

    await interaction.response.edit_message(embed=embed, view=self)
    await interaction.followup.send(
        f"Die Bewerbung wurde von {interaction.user.mention} **abgelehnt**."
    )


# ==========================================
# 4. DASHBOARD BUTTON (STARTET BEWERBUNG)
# ==========================================
class ApplyDashboardView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="Bewerbung starten 📝",
      style=discord.ButtonStyle.blurple,
      custom_id="start_apply_btn",
  )
  async def start_apply(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user

    try:
      dm_channel = await user.create_dm()
      await dm_channel.send(
          "Hallo! Wir starten jetzt deine Bewerbung. Ich werde dir"
          " nacheinander 20 Fragen stellen. Antworte einfach direkt auf meine"
          " Nachrichten.\n\n*Schreibe jetzt eine Nachricht, um die erste"
          " Frage zu starten.*"
      )
      await interaction.response.send_message(
          "Ich habe dir eine Privatnachricht gesendet!", ephemeral=True
      )
    except discord.Forbidden:
      await interaction.response.send_message(
          "Ich konnte dir keine Privatnachricht senden. Bitte aktiviere"
          " Direktnachrichten in deinen Discord-Einstellungen!",
          ephemeral=True,
      )
      return

    answers = []

    def check(m):
      return m.author == user and isinstance(m.channel, discord.DMChannel)

    for i, frage in enumerate(FRAGEN):
      await dm_channel.send(f"**Frage {i+1}/20:**\n{frage}")
      msg = await bot.wait_for("message", check=check)
      answers.append((frage, msg.content))

    await dm_channel.send(
        "Vielen Dank! Deine Bewerbung wurde erfolgreich abgesendet."
    )

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
      try:
        log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
      except Exception as e:
        print(f"[FEHLER] Log-Kanal konnte nicht geladen werden: {e}")
        await dm_channel.send(
            "⚠️ Fehler: Der Bewerbungskanal wurde nicht gefunden. Bitte"
            " informiere das Team!"
        )
        return

    if log_channel:
      embed = discord.Embed(
          title=f"Neue Bewerbung von {user.name} ({user.id})",
          color=discord.Color.blue(),
      )
      embed.set_thumbnail(url=user.display_avatar.url)

      for frage, antwort in answers:
        antwort_text = antwort[:1000] if antwort else "Keine Antwort"
        embed.add_field(name=frage, value=antwort_text, inline=False)

      try:
        await log_channel.send(embed=embed, view=ReviewView())
        print(f"[INFO] Bewerbung von {user.name} gesendet.")
      except Exception as e:
        print(f"[FEHLER] Konnte nicht in den Kanal senden: {e}")


# ==========================================
# 5. EVENTS & BEFEHLE
# ==========================================
@bot.event
async def setup_hook():
  try:
    await bot.load_extension("ranks")
  except Exception:
    pass


@bot.event
async def on_ready():
  bot.add_view(ApplyDashboardView())
  bot.add_view(ReviewView())

  guild = discord.Object(id=GUILD_ID)
  bot.tree.copy_global_to(guild=guild)
  await bot.tree.sync(guild=guild)

  print(f"Bot erfolgreich gestartet als: {bot.user}")


@bot.tree.command(
    name="setup_dashboard",
    description="Erstellt das Bewerbungs-Portal im aktuellen Kanal",
)
@app_commands.checks.has_permissions(administrator=True)
async def setup_dashboard(interaction: discord.Interaction):
  embed = discord.Embed(
      title="Bewerbungs-Portal",
      description=(
          "Klicke auf den Button unten, um deine Bewerbung per Privatnachricht"
          " zu starten."
      ),
      color=discord.Color.gold(),
  )
  await interaction.response.send_message(embed=embed, view=ApplyDashboardView())


# ==========================================
# 6. STARTEN DES BOTS UND WEBSERVERS
# ==========================================
keep_alive()
bot.run(TOKEN)