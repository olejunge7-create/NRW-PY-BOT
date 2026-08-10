import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

FRAK_FILE = os.path.abspath("fraktionen_data.json")

# Zentraler Speicher im Arbeitsspeicher als Fallback gegen Render-Resets
memory_fraktionen = {}

def load_fraktionen():
    global memory_fraktionen
    if os.path.exists(FRAK_FILE):
        try:
            with open(FRAK_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    memory_fraktionen = json.loads(content)
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
    return memory_fraktionen

def save_fraktionen(data):
    global memory_fraktionen
    memory_fraktionen = data
    try:
        with open(FRAK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

# Direkt beim Start laden
load_fraktionen()

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
                try:
                    if datetime.fromisoformat(w["ablauf"]) > now:
                        valid_warns.append(w)
                    else:
                        changed = True
                except:
                    pass
            if len(valid_warns) != len(info.get("warns", [])):
                info["warns"] = valid_warns
                changed = True
                
        if changed:
            save_fraktionen(data)

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    @app_commands.describe(name="Name der Fraktion", besitzer="Name oder Mention des Besitzers", link="Discord Einladungslink", standort="Standort / Nummer")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str, standort: str):
        await interaction.response.defer(ephemeral=True)
        data = load_fraktionen()
        
        data[name] = {
            "besitzer": besitzer,
            "link": link,
            "standort": standort,
            "warns": []
        }
        save_fraktionen(data)
        
        embed = discord.Embed(
            title="🏢 Fraktion hinzugefügt",
            description=f"Die Fraktion **{name}** wurde erfolgreich gespeichert!",
            color=discord.Color.green()
        )
        embed.add_field(name="Leitung", value=besitzer, inline=True)
        embed.add_field(name="Standort", value=standort, inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

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
            await interaction.followup.send(f"❌ Die Fraktion **{name}** wurde nicht gefunden!", ephemeral=True)
            return
            
        ablauf = datetime.now() + timedelta(days=tage)
        data[name]["warns"].append({"grund": grund, "ablauf": ablauf.isoformat()})
        
        anzahl = len(data[name]["warns"])
        status_text = f"⚠️ **{anzahl}/3 Warns aktiv**"
        if anzahl >= 3:
            data[name]["warns"] = []
            status_text = "🔴 **3/3 Limit erreicht!** Warns wurden zurückgesetzt."
            
        save_fraktionen(data)
        
        embed = discord.Embed(
            title=f"⚠️ Offizielle Verwarnung: {name}",
            color=discord.Color.red()
        )
        embed.add_field(name="Grund", value=grund, inline=False)
        embed.add_field(name="Gültigkeit", value=f"{tage} Tage (Bis: {ablauf.strftime('%d.%m.%Y')})", inline=True)
        embed.add_field(name="Status", value=status_text, inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="frakliste", description="Zeigt die offizielle Fraktionsliste im Clean-Stil.")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_fraktionen()
        
        if not data:
            await interaction.followup.send("Aktuell sind keine Fraktionen eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📋 FRAKTIONSLISTE",
            color=discord.Color.from_rgb(40, 43, 48)
        )
        
        for name, info in data.items():
            warns = info.get("warns", [])
            anzahl = len(warns)
            
            if anzahl == 0:
                warn_text = "✅ Keine Warns (0/3)"
            else:
                warn_text = f"⚠️ **{anzahl}/3 Warns**\n"
                for w in warns:
                    warn_text += f"      • {w['grund']} *(bis {w['ablauf'][:10]})*\n"
            
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