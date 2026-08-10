import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PARTNER_FILE = "partner_data.json"

def load_partner():
    if os.path.exists(PARTNER_FILE):
        try:
            with open(PARTNER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_partner(data):
    with open(PARTNER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class PartnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addpartner", description="Füge einen neuen Partner hinzu.")
    @app_commands.describe(name="Name des Servers", ansprechpartner="Ansprechpartner / Leitung", link="Discord Einladungslink")
    async def addpartner(self, interaction: discord.Interaction, name: str, ansprechpartner: str, link: str):
        await interaction.response.defer(ephemeral=True)
        
        data = load_partner()
        
        if name in data:
            await interaction.followup.send(f"❌ Der Partner **{name}** existiert bereits!", ephemeral=True)
            return
            
        data[name] = {
            "ansprechpartner": ansprechpartner,
            "link": link
        }
        save_partner(data)
        
        embed = discord.Embed(
            title="🤝 Partner hinzugefügt",
            description=f"Der Partner **{name}** wurde erfolgreich eingetragen.",
            color=discord.Color.green()
        )
        embed.add_field(name="Leitung", value=ansprechpartner, inline=True)
        embed.add_field(name="Discord", value=link, inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="delpartner", description="Lösche einen Partner aus der Liste.")
    @app_commands.describe(name="Name des Partners")
    async def delpartner(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        
        data = load_partner()
        if name not in data:
            await interaction.followup.send("❌ Partner nicht gefunden.", ephemeral=True)
            return
            
        del data[name]
        save_partner(data)
        
        await interaction.followup.send(f"🗑️ Der Partner **{name}** wurde entfernt.", ephemeral=True)

    @app_commands.command(name="partnerliste", description="Zeigt die offizielle Partner-Liste.")
    async def partnerliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        data = load_partner()
        if not data:
            await interaction.followup.send("Aktuell sind keine Partnerschaften eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📋 PARTNERSCHAFTSLISTE",
            color=discord.Color.from_rgb(40, 43, 48)
        )
        
        for name, info in data.items():
            value_block = (
                f"> 👑 **Leitung:** {info.get('ansprechpartner', 'Unbekannt')}\n"
                f"> 🔗 **Discord:** {info.get('link', 'Kein Link')}"
            )
            embed.add_field(name=f"✅ {name}", value=value_block, inline=False)
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PartnerCog(bot))