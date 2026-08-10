import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

PARTNER_DB = "partner.db"

def init_partner_db():
    conn = sqlite3.connect(PARTNER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner (
            name TEXT PRIMARY KEY,
            ansprechpartner TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_partner_db()

class PartnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addpartner", description="Füge einen neuen Partner hinzu.")
    @app_commands.describe(name="Name des Servers", ansprechpartner="Ansprechpartner / Leitung", link="Discord Einladungslink")
    async def addpartner(self, interaction: discord.Interaction, name: str, ansprechpartner: str, link: str):
        await interaction.response.defer(ephemeral=True)
        
        conn = sqlite3.connect(PARTNER_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM partner WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            await interaction.followup.send(f"❌ Der Partner **{name}** existiert bereits!", ephemeral=True)
            return
            
        cursor.execute("INSERT INTO partner (name, ansprechpartner, link) VALUES (?, ?, ?)", (name, ansprechpartner, link))
        conn.commit()
        conn.close()
        
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
        
        conn = sqlite3.connect(PARTNER_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM partner WHERE name = ?", (name,))
        if not cursor.fetchone():
            conn.close()
            await interaction.followup.send("❌ Partner nicht gefunden.", ephemeral=True)
            return
            
        cursor.execute("DELETE FROM partner WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        
        await interaction.followup.send(f"🗑️ Der Partner **{name}** wurde entfernt.", ephemeral=True)

    @app_commands.command(name="partnerliste", description="Zeigt die offizielle Partner-Liste im Fraktions-Stil.")
    async def partnerliste(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        conn = sqlite3.connect(PARTNER_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, ansprechpartner, link FROM partner")
        partner_eintraege = cursor.fetchall()
        conn.close()
        
        if not partner_eintraege:
            await interaction.followup.send("Aktuell sind keine Partnerschaften eingetragen.", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="📋 PARTNERSCHAFTSLISTE",
            color=discord.Color.from_rgb(40, 43, 48) # Dunkler, cleaner Look passend zum Bild
        )
        
        for name, ansprechpartner, link in partner_eintraege:
            # Hier bauen wir exakt denselben Stil nach wie bei deinen Fraktionen
            value_block = (
                f"> 👑 **Leitung:** {ansprechpartner}\n"
                f"> 🔗 **Discord:** {link}"
            )
            embed.add_field(name=f"✅ {name}", value=value_block, inline=False)
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(PartnerCog(bot))