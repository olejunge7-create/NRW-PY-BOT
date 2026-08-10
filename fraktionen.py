import discord
from discord.ext import commands
from discord import app_commands
import json

STORAGE_CHANNEL_ID = 1536159967323627631 # Stelle sicher, dass hier deine ID steht

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_data(self, channel):
        async for msg in channel.history(limit=10):
            if msg.author == self.bot.user and msg.content.startswith("{"):
                return msg, json.loads(msg.content)
        return None, {}

    @app_commands.command(name="addfrak", description="Erstelle eine neue Fraktion")
    async def addfrak(self, interaction: discord.Interaction, name: str, inhaber: str, discord_link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
        if not channel:
            await interaction.followup.send("❌ Fehler: Speicher-Kanal nicht gefunden!", ephemeral=True)
            return

        msg, data = await self.get_data(channel)
        data[name.upper()] = {
            "inhaber": inhaber,
            "link": discord_link,
            "standort": standort,
            "warns": 0
        }
        
        new_content = json.dumps(data)
        if msg:
            await msg.edit(content=new_content)
        else:
            await channel.send(new_content)
        
        await interaction.followup.send(f"✅ Fraktion **{name.upper()}** wurde gespeichert!", ephemeral=True)

    @app_commands.command(name="frakliste", description="Zeigt die offizielle Fraktionsliste")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
        _, data = await self.get_data(channel)
        
        if not data:
            await interaction.followup.send("📂 Es sind aktuell keine Fraktionen eingetragen.")
            return

        embed = discord.Embed(title="🏢 NOTRUF EMDEN | FRAKTIONSLISTE", color=discord.Color.blue())
        for name, info in data.items():
            warns = info.get("warns", 0)
            status = "✅" if warns < 3 else "❌"
            embed.add_field(
                name=f"─── {name} ───",
                value=f"👤 **Inhaber:** `{info['inhaber']}`\n🔗 **Discord:** {info['link']}\n📍 **Standort:** `{info['standort']}`\n🛡️ **Warns:** {warns}/3 {status}",
                inline=False
            )
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))