import discord
from discord.ext import commands
from discord import app_commands
json
class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_storage_channel(self, guild):
        # Sucht automatisch nach einem Kanal, der "datenban" oder "datenbank" heißt
        for channel in guild.text_channels:
            if "datenban" in channel.name.lower():
                return channel
        return None

    async def get_data(self, channel):
        async for msg in channel.history(limit=10):
            if msg.author == self.bot.user and msg.content.startswith("{"):
                return msg, json.loads(msg.content)
        return None, {}

    @app_commands.command(name="addfrak", description="Erstelle eine neue Fraktion")
    async def addfrak(self, interaction: discord.Interaction, name: str, inhaber: str, discord_link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        
        channel = await self.get_storage_channel(interaction.guild)
        if not channel:
            await interaction.followup.send("❌ Fehler: Konnte keinen Kanal finden, der 'datenban' heißt!", ephemeral=True)
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
        
        channel = await self.get_storage_channel(interaction.guild)
        if not channel:
            await interaction.followup.send("❌ Fehler: Speicher-Kanal nicht gefunden!")
            return

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