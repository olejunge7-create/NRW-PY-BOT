import discord
from discord.ext import commands
from discord import app_commands
import json
import os

WARN_FILE = "warns.json"
memory_warns = {}

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
        
        kick_status = ""
        
        # Prüfen, ob es der 3. Warn ist
        if anzahl >= 3:
            # Alle Warns zurücksetzen
            data[user_id_str] = []
            save_warns(data)
            
            # Versuchen den User zu kicken
            try:
                await user.kick(reason="3/3 Verwarnungen erreicht.")
                kick_status = "\n\n🔴 **Limit erreicht (3/3):** Alle Warns wurden gelöscht und der User wurde gekickt!"
            except Exception:
                kick_status = "\n\n⚠️ **Limit erreicht (3/3):** Warns wurden gelöscht, aber der Bot konnte den User nicht kicken (fehlende Rechte / Höherer Rang)."
        else:
            save_warns(data)
        
        embed = discord.Embed(
            title="⚠️ User verwarnt",
            description=f"**User:** {user.mention}\n**Grund:** {grund}\n**Anzahl Warns:** {anzahl}/3{kick_status}",
            color=discord.Color.red() if anzahl >= 3 else discord.Color.orange()
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