import discord
from discord.ext import commands
import json
import os

WARNINGS_FILE = "warnings.json"

def load_warnings():
    if os.path.exists(WARNINGS_FILE):
        try:
            with open(WARNINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_warnings(data):
    with open(WARNINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="warn", description="Verwarnt einen Benutzer.")
    @discord.app_commands.describe(member="Der Benutzer, der verwarnt werden soll", reason="Der Grund für die Verwarnung")
    @discord.app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        warnings = load_warnings()
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings:
            warnings[guild_id] = {}
        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []

        warnings[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(interaction.user)
        })

        save_warnings(warnings)

        total_warns = len(warnings[guild_id][user_id])

        embed = discord.Embed(
            title="⚠️ Verwarnung erhalten",
            description=f"Du wurdest auf **{interaction.guild.name}** verwarnt.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Grund", value=reason, inline=False)
        embed.add_field(name="Anzahl Verwarnungen", value=str(total_warns), inline=False)

        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

        await interaction.response.send_message(f"✅ {member.mention} wurde erfolgreich verwarnt! (Gesamt: {total_warns})", ephemeral=True)

    @discord.app_commands.command(name="warnings", description="Zeigt die Verwarnungen eines Benutzers an.")
    @discord.app_commands.describe(member="Der Benutzer, dessen Verwarnungen du sehen möchtest")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        warnings = load_warnings()
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        user_warns = warnings.get(guild_id, {}).get(user_id, [])

        if not user_warns:
            await interaction.response.send_message(f"{member.mention} hat keine Verwarnungen.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚠️ Verwarnungen für {member.display_name}",
            color=discord.Color.red()
        )

        for i, w in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warnung #{i}",
                value=f"**Grund:** {w['reason']}\n**Von:** {w['moderator']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))