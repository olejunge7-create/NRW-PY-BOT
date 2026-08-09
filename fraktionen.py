import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "fraktionen.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraktionen (
            name TEXT PRIMARY KEY,
            besitzer TEXT,
            link TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fraktion TEXT,
            grund TEXT,
            ablauf TEXT,
            FOREIGN KEY (fraktion) REFERENCES fraktionen (name) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class FraktionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_warns.start()

    def cog_unload(self):
        self.check_warns.cancel()

    @tasks.loop(minutes=60)
    async def check_warns(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM warns WHERE ablauf <= ?", (now,))
        conn.commit()
        conn.close()

    @app_commands.command(name="addfrak", description="Füge eine neue Fraktion hinzu.")
    @app_commands.describe(name="Name der Fraktion", besitzer="Name oder Mention des Besitzers", link="Discord Einladungslink")
    async def addfrak(self, interaction: discord.Interaction, name: str, besitzer: str, link: str):
        await interaction.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fraktionen WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            await interaction.followup.send(f"❌ Die Fraktion **{name}** existiert bereits!", ephemeral=True)
            return
            
        cursor.execute("INSERT INTO fraktionen (name, besitzer, link) VALUES (?, ?, ?)", (name, besitzer, link))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🏢 Neue Fraktion registriert",
            description=f"Die Fraktion **{name}** wurde erfolgreich hinzugefügt.",
            color=discord.Color.green()
        )
        embed.add_field(name="👑 Leitung", value=besitzer, inline=True)
        embed.add_field(name="🔗 Discord", value=f"[Zum Discord-Server]({link})", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="delfrak", description="Lösche eine Fraktion komplett.")
    @app_commands.describe(name="Name der Fraktion")
    async def delfrak(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fraktionen WHERE name = ?", (name,))
        if not cursor.fetchone():
            conn.close()
            await interaction.followup.send("❌ Fraktion nicht gefunden.", ephemeral=True)
            return
            
        cursor.execute("DELETE FROM fraktionen WHERE name = ?", (name,))
        cursor.execute("DELETE FROM warns WHERE fraktion = ?", (name,))
        conn.commit()
        conn.close()
        
        await interaction.followup.send(f"🗑️ Die Fraktion **{name}** wurde gelöscht.", ephemeral=True)

    @app_commands.command(name="frakwarn", description="Verwarne eine Fraktion (Max 3/3).")
    @app_commands.describe(name="Name der Fraktion", grund="Grund für den Warn", tage="Wie viele Tage gültig")
    async def frakwarn(self, interaction: discord.Interaction, name: str, grund: str, tage: int):
        await interaction.response.defer()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fraktionen WHERE name = ?", (name,))
        if not cursor.fetchone():
            conn.close()
            await interaction.followup.send(f"❌ Die Fraktion **{name}** wurde nicht gefunden!", ephemeral=True)
            return
            
        ablauf = datetime.now() + timedelta(days=tage)
        cursor.execute("INSERT INTO warns (fraktion, grund, ablauf) VALUES (?, ?, ?)", (name, grund, ablauf.isoformat()))
        
        cursor.execute("SELECT COUNT(*) FROM warns WHERE fraktion = ?", (name,))
        anzahl = cursor.fetchone()[0]
        
        status_text = f"⚠️ **{anzahl}/3 Warns aktiv**"
        if anzahl >= 3:
            cursor.execute("DELETE FROM warns WHERE fraktion = ?", (name,))
            status_text = "🔴 **3/3 Limit erreicht!** Warns wurden zurückgesetzt (Sanktion folgt)."
            
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title=f"⚠️ Offizielle Verwarnung: {name}",
            color=discord.Color.red()
        )
        embed.add_field(name="Grund", value=grund, inline=False)
        embed.add_field(name="Gültigkeit", value=f"{tage} Tage (Gültig bis: {ablauf.strftime('%d.%m.%Y')})", inline=True)
        embed.add_field(name="Aktueller Status", value=status_text, inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="frakliste", description="Zeigt die offizielle Fraktionsübersicht.")
    async def frakliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, besitzer, link FROM fraktionen")
        fraktionen = cursor.fetchall()
        
        if not fraktionen:
            conn.close()
            await interaction.followup.send("Aktuell sind keine Fraktionen eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="⚡ STAATLICHE & ZIVILE FRAKTIONEN",
            description="Übersicht aller registrierten Fraktionen, Leitungen und des aktuellen Status.",
            color=discord.Color.from_rgb(30, 144, 255)
        )
        
        for name, besitzer, link in fraktionen:
            cursor.execute("SELECT grund, ablauf FROM warns WHERE fraktion = ?", (name,))
            warns = cursor.fetchall()
            anzahl = len(warns)
            
            if anzahl == 0:
                warn_text = "Keine (0/3)"
            else:
                warn_text = f"**{anzahl}/3 Warns**\n"
                for grund, ablauf in warns:
                    warn_text += f"• {grund} *(bis {ablauf[:10]})*\n"
            
            value_block = (
                f"• **Leitung:** {besitzer}\n"
                f"• **Discord:** {link}\n"
                f"• **Warns:** {warn_text}"
            )
            
            embed.add_field(name=f"🔹 {name}", value=value_block, inline=False)
            
        conn.close()
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FraktionCog(bot))