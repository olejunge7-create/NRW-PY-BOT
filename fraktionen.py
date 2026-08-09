import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

FRAK_FILE = "fraktionen_data.json"

def load_fraktionen():
    if os.path.exists(FRAK_FILE):
        try:
            with open(FRAK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_fraktionen(data):
    with open(FRAK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_warns.start()

    def cog_unload(self):
        self.check_warns.cancel()

    @tasks.loop(minutes=60)
    async def check_warns(self):
        data = load_fraktionen()
        changed = False
        now = datetime.now()
        
        for frak_name, info in data.items():
            valid_warns = []
            for w in info.get("warns", []):
                if datetime.fromisoformat(w["ablauf"]) > now:
                    valid_warns.append(w)
                else:
                    changed = True
            if len(valid_warns) != len(info.get("warns", [])):
                info["warns"] = valid_warns
                changed = True
                
        if changed:
            save_fraktionen(data)

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    @app_commands.describe(name="Name der Fraktion", besitzer="Name oder Mention des Besitzers", link="Discord Einladungslink")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str):
        await interaction.response.defer(ephemeral=True)
        data = load_fraktionen()
        
        if name in data:
            await interaction.followup.send(f"❌ Die Fraktion **{name}** existiert bereits!", ephemeral=True)
            return
            
        data[name] = {
            "besitzer": besitzer,
            "link": link,
            "warns": []
        }
        save_fraktionen(data)
        
        embed = discord.Embed(title="✅ Fraktion hinzugefügt", color=discord.Color.green())
        embed.add_field(name="Fraktion", value=name, inline=True)
        embed.add_field(name="Besitzer", value=besitzer, inline=True)
        embed.add_field(name="Discord", value=link, inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delfrak", description="Lösche eine Fraktion komplett.")
    @app_commands.describe(name="Name der Fraktion")
    async def delfrak(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        data = load_fraktionen()
        if name in data:
            del data[name]
            save_fraktionen(data)
            await interaction.followup.send(f"🗑️ Die Fraktion **{name}** wurde gelöscht.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Fraktion nicht gefunden.", ephemeral=True)

    @app_commands.command(name="frakwarn", description="Verwarne eine Fraktion (Max 3/3).")
    @app_commands.describe(name="Name der Fraktion", grund="Grund für den Warn", tage="Wie viele Tage gültig")
    async def frakwarn(self, interaction: discord.Interaction, name: str, grund: str, tage: int):
        await interaction.response.defer()
        data = load_fraktionen()
        
        if name not in data:
            await interaction.followup.send(f"❌ Die Fraktion **{name}** wurde nicht gefunden! Erstelle sie zuerst mit `/addfrak`.", ephemeral=True)
            return
            
        ablauf = datetime.now() + timedelta(days=tage)
        data[name]["warns"].append({"grund": grund, "ablauf": ablauf.isoformat()})
        
        anzahl = len(data[name]["warns"])
        
        status_text = f"Anzahl Warns: **{anzahl}/3**"
        if anzahl >= 3:
            data[name]["warns"] = []
            status_text = "🔴 **Limit 3/3 erreicht!** Alle Warns wurden zurückgesetzt (Frak-Sanktion fällig)."
            
        save_fraktionen(data)
        
        embed = discord.Embed(title="⚠️ Fraktions-Verwarnung", color=discord.Color.red())
        embed.add_field(name="Fraktion", value=name, inline=True)
        embed.add_field(name="Stand", value=status_text, inline=True)
        embed.add_field(name="Grund", value=grund, inline=False)
        embed.add_field(name="Gültigkeit", value=f"{tage} Tage (bis {ablauf.strftime('%d.%m.%Y')})", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="frakliste", description="Zeigt die große Fraktions- und Info-Liste.")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_fraktionen()
        if not data:
            await interaction.followup.send("✅ Aktuell sind keine Fraktionen eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(title="📋 Offizielle Fraktions- & Info-Liste", color=discord.Color.from_rgb(0, 150, 255))
        
        for name, info in data.items():
            warns = info.get("warns", [])
            anzahl = len(warns)
            
            if anzahl == 0:
                warn_text = "✅ Keine Warns (0/3)"
            else:
                warn_text = f"⚠️ **{anzahl}/3 Warns**\n"
                for w in warns:
                    warn_text += f"• {w['grund']} *(Läuft ab: {w['ablauf'][:10]})*\n"
            
            value_str = f"👑 **Besitzer:** {info.get('besitzer', 'Unbekannt')}\n" \
                        f"🔗 **Discord:** {info.get('link', 'Kein Link')}\n" \
                        f"🛡️ **Status:** {warn_text}"
            
            embed.add_field(name=f"📌 {name}", value=value_str, inline=False)
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))