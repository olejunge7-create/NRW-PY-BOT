import discord
from discord.ext import commands
from discord import app_commands
import json
import os

WARN_FILE = "warns.json"
memory_warns = {}

# Deine 21 Team-Rollen-IDs
TEAM_ROLLEN_IDS = [
    1534325338182520991,  # Rang 1
    1534325338182520992,  # Rang 2
    1534325338182520993,  # Rang 3
    1534325338182520994,  # Rang 4
    1534325338199556137,  # Rang 5
    1534325338199556138,  # Rang 6
    1534325338199556139,  # Rang 7
    1534325338199556140,  # Rang 8
    1534325338199556142,  # Rang 9
    1534325338199556143,  # Rang 10
    1534325338199556145,  # Rang 11
    1534325338199556146,  # Rang 12
    1534325338212007978,  # Rang 13
    1534325338212007979,  # Rang 14
    1534325338212007980,  # Rang 15
    1534325338212007981,  # Rang 16
    1534325338212007982,  # Rang 17
    1534325338212007983,  # Rang 18
    1534325338212007984,  # Rang 19
    1534325338212007985,  # Rang 20
    1534325338212007986   # Rang 21
]

def load_warns():
    global memory_warns
    if os.path.exists(WARN_FILE):
        try:
            with open(WARN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                memory_warns.update(data)
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
    return memory_warns

def save_warns(data):
    global memory_warns
    memory_warns = data
    try:
        with open(WARN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_warns()

    @app_commands.command(name="warn", description="Verwarne einen User.")
    @app_commands.describe(user="Der User", grund="Der Grund für den Warn")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, grund: str):
        data = load_warns()
        user_id_str = str(user.id)
        
        if user_id_str not in data:
            data[user_id_str] = []
            
        data[user_id_str].append(grund)
        anzahl = len(data[user_id_str])
        
        team_status = ""
        
        # Wenn das Limit von 3 Warns erreicht ist
        if anzahl >= 3:
            data[user_id_str] = []
            save_warns(data)
            
            # Alle Team-Rollen der Liste entfernen, die der User besitzt
            entfernte_rollen = 0
            for rolle_id in TEAM_ROLLEN_IDS:
                role = interaction.guild.get_role(rolle_id)
                if role and role in user.roles:
                    try:
                        await user.remove_roles(role, reason="3/3 Verwarnungen erreicht - Team-Rollen entzogen.")
                        entfernte_rollen += 1
                    except Exception:
                        pass
            
            team_status = f"\n\n🔴 **Limit erreicht (3/3):** Warns zurückgesetzt und {entfernte_rollen} Team-Rolle(n) entzogen!"
            
            embed = discord.Embed(
                title="⚠️ User verwarnt (Team-Rollen entzogen)",
                description=f"**User:** {user.mention}\n**Grund:** {grund}\n**Anzahl Warns:** 3/3{team_status}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        save_warns(data)
        
        embed = discord.Embed(
            title="⚠️ User verwarnt",
            description=f"**User:** {user.mention}\n**Grund:** {grund}\n**Anzahl Warns:** {anzahl}/3",
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
            title=f"⚠️ Verwarnungen von {user.name} (Gesamt: {len(user_warns)}/3)",
            description=warn_text,
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCog(bot))