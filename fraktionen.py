import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

FRAK_WARN_FILE = "frak_warns.json"

# Deine festen Fraktionen
FRAKTIONEN = [
    "NRW Polizei", 
    "Feuerwehr", 
    "Medics", 
    "LSPD", 
    "Gang", 
    "Andere"
]

def load_frak_warns():
    if os.path.exists(FRAK_WARN_FILE):
        with open(FRAK_WARN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_frak_warns(data):
    with open(FRAK_WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_warns.start()

    def cog_unload(self):
        self.check_warns.cancel()

    @tasks.loop(minutes=60)
    async def check_warns(self):
        data = load_frak_warns()
        changed = False
        now = datetime.now()
        for frak in list(data.keys()):
            valid_warns = [w for w in data[frak] if datetime.fromisoformat(w["ablauf"]) > now]
            if not valid_warns:
                del data[frak]
                changed = True
            elif len(valid_warns) != len(data[frak]):
                data[frak] = valid_warns
                changed = True
        if changed: save_frak_warns(data)

    # Befehl mit Auswahlmenü für die Fraktionen
    @app_commands.command(name="frakwarn", description="Verwarne eine Fraktion.")
    @app_commands.choices(fraktion=[app_commands.Choice(name=f, value=f) for f in FRAKTIONEN])
    async def frakwarn(self, interaction: discord.Interaction, fraktion: str, grund: str, tage: int):
        data = load_frak_warns()
        if fraktion not in data: data[fraktion] = []
            
        ablauf = datetime.now() + timedelta(days=tage)
        data[fraktion].append({"grund": grund, "ablauf": ablauf.isoformat()})
        save_frak_warns(data)
        
        await interaction.response.send_message(f"⚠️ **{fraktion}** wurde für **{tage} Tage** verwarnt.\nGrund: {grund}")

    @app_commands.command(name="frakliste", description="Zeige alle Fraktions-Warns.")
    async def frakliste(self, interaction: discord.Interaction):
        data = load_frak_warns()
        if not data:
            await interaction.response.send_message("✅ Keine aktiven Fraktions-Warns.", ephemeral=True)
            return
            
        embed = discord.Embed(title="📋 Aktive Fraktions-Warns", color=discord.Color.blue())
        for frak, warns in data.items():
            warn_str = "\n".join([f"• {w['grund']} (Läuft ab: {w['ablauf'][:10]})" for w in warns])
            embed.add_field(name=frak, value=warn_str, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))