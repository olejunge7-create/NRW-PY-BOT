import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta

STORAGE_CHANNEL_ID = 1536159967323627631

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}

    async def sync_to_discord(self):
        try:
            channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
            if not channel:
                print("❌ Warnung: Speicher-Kanal für Fraktionen nicht gefunden!")
                return
            
            # Alte Bot-Nachrichten löschen
            async for msg in channel.history(limit=5):
                if msg.author == self.bot.user:
                    await msg.delete()
            
            content = json.dumps(self.data, ensure_ascii=False)
            await channel.send(content)
        except Exception as e:
            print(f"❌ Fehler beim Sync in Discord: {e}")

    async def load_from_discord(self):
        try:
            channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
            if not channel:
                return
            
            async for msg in channel.history(limit=5):
                if msg.author == self.bot.user:
                    try:
                        self.data = json.loads(msg.content)
                        return
                    except:
                        pass
            self.data = {}
        except Exception as e:
            print(f"❌ Fehler beim Laden aus Discord: {e}")
            self.data = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_from_discord()

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    @app_commands.describe(name="Name der Fraktion", besitzer="Leitung", link="Discord Link", standort="Standort")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        await self.load_from_discord()
        
        self.data[name] = {
            "besitzer": besitzer,
            "link": link,
            "standort": standort,
            "warns": []
        }
        await self.sync_to_discord()
        
        embed = discord.Embed(
            title="🏢 Fraktion hinzugefügt",
            description=f"Die Fraktion **{name}** wurde gespeichert!",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="delfrak", description="Lösche eine Fraktion komplett.")
    @app_commands.describe(name="Name der Fraktion")
    async def delfrak(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        await self.load_from_discord()
        
        if name in self.data:
            del self.data[name]
            await self.sync_to_discord()
            await interaction.followup.send(f"🗑️ Die Fraktion **{name}** wurde gelöscht.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Fraktion nicht gefunden.", ephemeral=True)

    @app_commands.command(name="frakliste", description="Zeigt die offizielle Fraktionsliste.")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.load_from_discord()
        
        if not self.data:
            await interaction.followup.send("Aktuell sind keine Fraktionen eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📋 FRAKTIONSLISTE",
            color=discord.Color.from_rgb(40, 43, 48)
        )
        
        for name, info in self.data.items():
            warns = info.get("warns", [])
            anzahl = len(warns)
            
            if anzahl == 0:
                warn_text = "✅ Keine Warns (0/3)"
            else:
                warn_text = f"⚠️ **{anzahl}/3 Warns**"
            
            value_block = (
                f"> 👑 **Leitung:** {info.get('besitzer', 'Unbekannt')}\n"
                f"> 🔗 **Discord:** {info.get('link', 'Kein Link')}\n"
                f"> 📍 **Standort:** {info.get('standort', 'Unbekannt')}\n"
                f"> 🛡️ **Status:** {warn_text}"
            )
            
            embed.add_field(name=f"✅ {name}", value=value_block, inline=False)
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))