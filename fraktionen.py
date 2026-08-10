import discord
from discord.ext import commands
from discord import app_commands
import json
import os

FILE_NAME = "fraktionen.json"

def load_data():
    if not os.path.exists(FILE_NAME):
        return {}
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    @app_commands.describe(name="Name", besitzer="Leitung", link="Link", standort="Standort")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        
        data[name] = {
            "besitzer": besitzer,
            "link": link,
            "standort": standort,
            "warns": []
        }
        save_data(data)
        
        embed = discord.Embed(
            title="🏢 Fraktion hinzugefügt",
            description=f"Die Fraktion **{name}** wurde gespeichert!",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="delfrak", description="Lösche eine Fraktion.")
    @app_commands.describe(name="Name")
    async def delfrak(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        
        if name in data:
            del data[name]
            save_data(data)
            await interaction.followup.send(f"🗑️ **{name}** wurde gelöscht.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Nicht gefunden.", ephemeral=True)

    @app_commands.command(name="frakliste", description="Zeigt die Fraktionsliste.")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        
        if not data:
            await interaction.followup.send("Aktuell sind keine Fraktionen eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(title="📋 FRAKTIONSLISTE", color=discord.Color.from_rgb(40, 43, 48))
        
        for name, info in data.items():
            warns = info.get("warns", [])
            warn_text = "✅ Keine Warns (0/3)" if not warns else f"⚠️ {len(warns)}/3 Warns"
            
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