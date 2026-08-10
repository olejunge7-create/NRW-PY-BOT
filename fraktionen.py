import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime, timedelta

# HIER DEINE KANAL-ID EINTRAGEN:
STORAGE_CHANNEL_ID = 1536159967323627631 

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.check_warns.start()

    async def sync_to_discord(self):
        channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
        if not channel: return
        
        # Alte Nachrichten löschen, damit wir immer die aktuellste haben
        async for msg in channel.history(limit=5):
            if msg.author == self.bot.user:
                await msg.delete()
        
        content = json.dumps(self.data)
        await channel.send(content)

    async def load_from_discord(self):
        channel = self.bot.get_channel(STORAGE_CHANNEL_ID)
        if not channel: return
        
        async for msg in channel.history(limit=1):
            if msg.author == self.bot.user:
                self.data = json.loads(msg.content)
                return
        self.data = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_from_discord()

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        self.data[name] = {"besitzer": besitzer, "link": link, "standort": standort, "warns": []}
        await self.sync_to_discord()
        await interaction.followup.send("✅ Gespeichert!", ephemeral=True)

    @app_commands.command(name="frakliste", description="Zeigt die Fraktionsliste.")
    async def frakliste(self, interaction: discord.Interaction):
        await self.load_from_discord() # Immer aktuell ziehen
        if not self.data:
            await interaction.response.send_message("Keine Daten vorhanden.", ephemeral=True)
            return
            
        embed = discord.Embed(title="📋 FRAKTIONSLISTE", color=discord.Color.from_rgb(40, 43, 48))
        for name, info in self.data.items():
            warns = info.get("warns", [])
            w_text = f"✅ Keine Warns (0/3)" if not warns else f"⚠️ {len(warns)}/3 Warns"
            value_block = f"> 👑 **Leitung:** {info['besitzer']}\n> 🔗 **Discord:** {info['link']}\n> 📍 **Standort:** {info['standort']}\n> 🛡️ **Status:** {w_text}"
            embed.add_field(name=f"✅ {name}", value=value_block, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))