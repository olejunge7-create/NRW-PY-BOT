import discord
from discord.ext import commands
from discord import app_commands
import json
import os

WARN_FILE = "warns.json"

def load_warns():
    if os.path.exists(WARN_FILE):
        try:
            with open(WARN_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_warns(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Verwarne einen User.")
    @app_commands.describe(user="Der User", grund="Der Grund für den Warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, grund: str):
        data = load_warns()
        user_id_str = str(user.id)
        
        if user_id_str not in data:
            data[user_id_str] = []
            
        data[user_id_str].append(grund)
        save_warns(data)
        
        embed = discord.Embed(
            title="⚠️ User verwarnt",
            description=f"**User:** {user.mention}\n**Grund:** {grund}\n**Anzahl Warns:** {len(data[user_id_str])}",
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
        warn_text = "\n".join([f"{i+1}. {w}" for i, w in enumerate(user_warns)])
        
        embed = discord.Embed(
            title=f"⚠️ Verwarnungen von {user.name}",
            description=warn_text,
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))