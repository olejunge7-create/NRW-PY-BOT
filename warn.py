import discord
from discord.ext import commands
from discord import app_commands
import json
import os

WARN_FILE = "warns.json"

def load_warns():
    if os.path.exists(WARN_FILE):
        try:
            with open(WARN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Warns: {e}")
            return {}
    return {}

def save_warns(data):
    with open(WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Verwarne einen User.")
    @app_commands.describe(user="Der User", grund="Der Grund für den Warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, grund: str):
        data = load_warns()
        user_id_str = str(user.id)
        
        # Sicherstellen, dass die Liste für den User existiert
        if user_id_str not in data:
            data[user_id_str] = []
            
        # Warnung zur Liste hinzufügen
        data[user_id_str].append(grund)
        save_warns(data)
        
        anzahl = len(data[user_id_str])
        
        embed = discord.Embed(
            title="⚠️ User verwarnt",
            description=f"**User:** {user.mention}\n**Grund:** {grund}\n**Anzahl Warns:** {anzahl}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warns", description="Zeige die Warns eines Users an.")
    @app_commands.describe(user="Der User")
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        data = load_warns()
        user_id_str = str(user.id)
        
        if user_id_str not in data or not data[user_id_str]:
            await interaction.response.send_message(f"✅ {user.mention} hat keine Verwarnungen.", ephemeral=True)
            return
            
        user_warns = data[user_id_str]
        warn_text = "\n".join([f"• {w}" for i, w in enumerate(user_warns)])
        
        embed = discord.Embed(
            title=f"⚠️ Verwarnungen von {user.name} (Gesamt: {len(user_warns)})",
            description=warn_text,
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))